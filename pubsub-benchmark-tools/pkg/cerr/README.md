# cerr
Short for constant error, `cerr` provides errors which can be compared in logic statements. For example:

```go
foo, err := getFoo()
if err != nil {
  if err == SpecialErr {
    // do something...
    return
  }

  // do something else
}
```
