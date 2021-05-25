package chain

import (
	"context"
	"errors"
	"fmt"
	"github.com/protolambda/zrnt/eth2/beacon"
	"github.com/protolambda/ztyp/tree"
)

type ColdChain interface {
	Start() Slot
	End() Slot
	OnFinalizedEntry(entry *HotEntry) error
	Chain
}

type FinalizedEntryView struct {
	slot     Slot
	finChain *FinalizedChain
}

func (e *FinalizedEntryView) Slot() Slot {
	return e.slot
}

func (e *FinalizedEntryView) IsEmpty() bool {
	return e.ParentRoot() == e.BlockRoot()
}

func (e *FinalizedEntryView) ParentRoot() (root Root) {
	return e.finChain.parentRoot(e.slot)
}

func (e *FinalizedEntryView) BlockRoot() (root Root) {
	return e.finChain.blockRoot(e.slot)
}

func (e *FinalizedEntryView) StateRoot() Root {
	return e.finChain.stateRoot(e.slot)
}

func (e *FinalizedEntryView) EpochsContext(ctx context.Context) (*beacon.EpochsContext, error) {
	return e.finChain.getEpochsContext(ctx, e.slot)
}

func (e *FinalizedEntryView) State(ctx context.Context) (*beacon.BeaconStateView, error) {
	return e.finChain.getState(ctx, e.slot)
}

type FinalizedChain struct {
	// Cache of pubkeys, may contain pubkeys that are not finalized,
	// but finalized state will not be in conflict with this cache.
	PubkeyCache *beacon.PubkeyCache
	// Start of the historical data
	AnchorSlot Slot

	// Block roots, starting at AnchorSlot
	// A blockRoot can be a copy of the previous root if current entry is empty
	BlockRoots []Root

	// State roots, starting at AnchorSlot
	StateRoots []Root

	// BlockRoots maps the canonical chain block roots to the block slot
	SlotsByBlockRoot map[Root]Slot
	// BlockRoots maps the canonical chain state roots to the state slot
	SlotsByStateRoot map[Root]Slot

	// Spec is holds configuration information for the parameters and types of the chain
	Spec *beacon.Spec
}

var _ = ColdChain((*FinalizedChain)(nil))

func NewFinalizedChain(anchorSlot Slot, spec *beacon.Spec) *FinalizedChain {
	initialCapacity := Slot(200)
	return &FinalizedChain{
		PubkeyCache:      beacon.EmptyPubkeyCache(),
		AnchorSlot:       anchorSlot,
		BlockRoots:       make([]Root, 0, initialCapacity),
		StateRoots:       make([]Root, 0, initialCapacity),
		SlotsByBlockRoot: make(map[Root]Slot, initialCapacity),
		SlotsByStateRoot: make(map[Root]Slot, initialCapacity),
		Spec:             spec,
	}
}

type ColdChainIter struct {
	Chain              Chain
	StartSlot, EndSlot Slot
}

func (fi *ColdChainIter) Start() Slot {
	return fi.StartSlot
}

func (fi *ColdChainIter) End() Slot {
	return fi.EndSlot
}

func (fi *ColdChainIter) Entry(slot Slot) (entry ChainEntry, err error) {
	if slot < fi.StartSlot || slot >= fi.EndSlot {
		return nil, fmt.Errorf("out of range slot: %d, range: [%d, %d)", slot, fi.StartSlot, fi.EndSlot)
	}
	entry, err = fi.Chain.BySlot(slot)
	return
}

func (f *FinalizedChain) Iter() (ChainIter, error) {
	start := f.Start()
	end := f.End()
	return &ColdChainIter{
		Chain:     f,
		StartSlot: start,
		EndSlot:   end,
	}, nil
}

func (f *FinalizedChain) Start() Slot {
	return f.AnchorSlot
}

func (f *FinalizedChain) End() Slot {
	return f.AnchorSlot + Slot(len(f.StateRoots))
}

var UnknownRootErr = errors.New("unknown root")

func (f *FinalizedChain) ByStateRoot(root Root) (ChainEntry, error) {
	slot, ok := f.SlotsByStateRoot[root]
	if !ok {
		return nil, UnknownRootErr
	}
	return f.BySlot(slot)
}

func (f *FinalizedChain) ByBlockRoot(root Root) (ChainEntry, error) {
	slot, ok := f.SlotsByBlockRoot[root]
	if !ok {
		return nil, UnknownRootErr
	}
	return f.BySlot(slot)
}

func (f *FinalizedChain) ClosestFrom(fromBlockRoot Root, toSlot Slot) (ChainEntry, error) {
	if start := f.Start(); toSlot < start {
		return nil, fmt.Errorf("slot %d is too early. Start is at slot %d", toSlot, start)
	}
	// check if the root is canonical
	_, ok := f.SlotsByStateRoot[fromBlockRoot]
	if !ok {
		return nil, UnknownRootErr
	}
	// find the slot closest to the requested slot: whatever is still within range
	if end := f.End(); end == 0 {
		return nil, errors.New("empty chain, no data available")
	} else if toSlot >= end {
		toSlot = end - 1
	}
	return f.BySlot(toSlot)
}

func (f *FinalizedChain) BySlot(slot Slot) (ChainEntry, error) {
	if start := f.Start(); slot < start {
		return nil, fmt.Errorf("slot %d is too early. Chain starts at slot %d", slot, start)
	}
	if end := f.End(); slot >= end {
		return nil, fmt.Errorf("slot %d is too late. Chain ends at slot %d", slot, end)
	}
	return &FinalizedEntryView{
		slot:     slot,
		finChain: f,
	}, nil
}

func (f *FinalizedChain) OnFinalizedEntry(entry *HotEntry) error {
	if end := f.End(); entry.slot != end {
		return fmt.Errorf("expected next finalized entry to have slot %d, but got %d from entry with block root %s",
			end, entry.slot, entry.blockRoot.String())
	}
	postStateRoot := entry.state.HashTreeRoot(tree.GetHashFn())
	f.BlockRoots = append(f.BlockRoots, entry.blockRoot)
	f.StateRoots = append(f.StateRoots, postStateRoot)
	f.SlotsByStateRoot[postStateRoot] = entry.slot
	if entry.parentRoot != entry.blockRoot {
		// if it's not an empty slot, remember it by block root
		f.SlotsByBlockRoot[entry.blockRoot] = entry.slot
	}
	return nil
}

func (f *FinalizedChain) parentRoot(slot Slot) (root Root) {
	if slot <= f.AnchorSlot {
		return Root{}
	}
	return f.BlockRoots[slot-1-f.AnchorSlot]
}

func (f *FinalizedChain) blockRoot(slot Slot) (root Root) {
	if slot < f.AnchorSlot {
		return Root{}
	}
	return f.BlockRoots[slot-f.AnchorSlot]
}

func (f *FinalizedChain) stateRoot(slot Slot) Root {
	if slot < f.AnchorSlot {
		return Root{}
	}
	return f.StateRoots[slot-f.AnchorSlot]
}

func (f *FinalizedChain) getEpochsContext(ctx context.Context, slot Slot) (*beacon.EpochsContext, error) {
	epc := &beacon.EpochsContext{
		PubkeyCache: f.PubkeyCache,
	}
	// We do not store shuffling for older epochs
	// TODO: maybe store it after all, for archive node functionality?
	state, err := f.getState(ctx, slot)
	if err != nil {
		return nil, err
	}
	if err := epc.LoadShuffling(state); err != nil {
		return nil, err
	}
	if err := epc.LoadProposers(state); err != nil {
		return nil, err
	}
	return epc, nil
}

func (f *FinalizedChain) getState(ctx context.Context, slot Slot) (*beacon.BeaconStateView, error) {
	return nil, errors.New("todo: load state from state storage")
}
