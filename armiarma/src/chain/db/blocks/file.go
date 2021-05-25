package blocks

import (
	"context"
	"encoding/hex"
	"fmt"
	"github.com/protolambda/zrnt/eth2/beacon"
	"github.com/protolambda/ztyp/codec"
	"io"
	"io/ioutil"
	"os"
	"path"
	"strings"
	"time"
)

type FileDB struct {
	spec     *beacon.Spec
	BasePath string
}

func (db *FileDB) rootToPath(root beacon.Root) string {
	return path.Join(db.BasePath, "0x"+hex.EncodeToString(root[:])+".ssz")
}

func (db *FileDB) Store(ctx context.Context, block *BlockWithRoot) (exists bool, err error) {
	outPath := db.rootToPath(block.Root)
	f, err := os.OpenFile(outPath, os.O_RDWR|os.O_CREATE|os.O_EXCL, 0755)
	defer f.Close()
	if err != nil {
		if os.IsExist(err) {
			return true, nil
		}
		return false, err
	}
	if err := block.Block.Serialize(db.spec, codec.NewEncodingWriter(f)); err != nil {
		return false, fmt.Errorf("failed to store block %s: %v", block.Root, err)
	}
	return false, nil
}

func (db *FileDB) Import(r io.Reader) (exists bool, err error) {
	buf := getPoolBlockBuf()
	defer dbBlockPool.Put(buf)
	if _, err := buf.ReadFrom(r); err != nil {
		return false, err
	}
	var dest beacon.SignedBeaconBlock
	err = dest.Deserialize(db.spec, codec.NewDecodingReader(buf, uint64(len(buf.Bytes()))))
	if err != nil {
		return false, fmt.Errorf("failed to decode block, nee valid block to get block root. Err: %v", err)
	}
	// Take the hash-tree-root of the BeaconBlock, ignore the signature.
	return db.Store(context.Background(), WithRoot(db.spec, &dest))
}

func (db *FileDB) Get(root beacon.Root, dest *beacon.SignedBeaconBlock) (exists bool, err error) {
	outPath := db.rootToPath(root)
	f, err := os.Open(outPath)
	defer f.Close()
	if err != nil {
		return false, err
	}
	info, err := f.Stat()
	if err != nil {
		return true, err
	}
	err = dest.Deserialize(db.spec, codec.NewDecodingReader(f, uint64(info.Size())))
	return true, err
}

func (db *FileDB) Size(root beacon.Root) (size uint64, exists bool) {
	outPath := db.rootToPath(root)
	f, err := os.Open(outPath)
	defer f.Close()
	if err != nil {
		return 0, false
	}
	info, err := f.Stat()
	if err != nil {
		return 0, false
	}
	return uint64(info.Size()), true
}

func (db *FileDB) Export(root beacon.Root, w io.Writer) (exists bool, err error) {
	outPath := db.rootToPath(root)
	f, err := os.Open(outPath)
	defer f.Close()
	if err != nil {
		return false, err
	}
	_, err = io.Copy(w, f)
	return true, err
}

func (db *FileDB) Stream(root beacon.Root) (r io.ReadCloser, size uint64, exists bool, err error) {
	outPath := db.rootToPath(root)
	f, err := os.Open(outPath)
	if err != nil {
		return nil, 0, false, err

	}
	info, err := f.Stat()
	if err != nil {
		return nil, 0, false, err
	}
	return f, uint64(info.Size()), true, nil
}

func (db *FileDB) Remove(root beacon.Root) (exists bool, err error) {
	outPath := db.rootToPath(root)
	err = os.Remove(outPath)
	if os.IsNotExist(err) {
		return false, nil
	}
	return true, err
}

func (db *FileDB) Stats() DBStats {
	files, err := ioutil.ReadDir(db.BasePath)
	if err != nil {
		return DBStats{}
	}
	// count files, and return latest write, and count of valid looking SSZ block files
	lastMod := beacon.Root{}
	lastModTime := time.Time{}
	count := 0
	for _, f := range files {
		if name := f.Name(); len(name) == 2+64+4 &&
			strings.HasPrefix(name, "0x") &&
			strings.HasSuffix(name, ".ssz") {
			root, err := hex.DecodeString(name[2 : 2+64])
			if err != nil {
				continue
			}
			if lastModTime.Before(f.ModTime()) {
				lastModTime = f.ModTime()
				copy(lastMod[:], root)
			}
			count += 1
		}
	}
	// return a copy (struct is small and has no pointers)
	return DBStats{
		Count:     0,
		LastWrite: beacon.Root{},
	}
}

func (db *FileDB) List() (out []beacon.Root) {
	files, err := ioutil.ReadDir(db.BasePath)
	if err != nil {
		return nil
	}
	out = make([]beacon.Root, 0, len(files))
	for _, f := range files {
		if name := f.Name(); len(name) == 2+64+4 &&
			strings.HasPrefix(name, "0x") &&
			strings.HasSuffix(name, ".ssz") {
			root, err := hex.DecodeString(name[2 : 2+64])
			if err != nil {
				continue
			}
			i := len(out)
			out = append(out, beacon.Root{})
			copy(out[i][:], root)
		}
	}
	return out
}

func (db *FileDB) Path() string {
	return db.BasePath
}

func (db *FileDB) Spec() *beacon.Spec {
	return db.spec
}
