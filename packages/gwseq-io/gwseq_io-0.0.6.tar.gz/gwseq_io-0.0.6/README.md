## Installation

```
pip install gwseq-io
```

Requires numpy and pybind11.

## Usage

### Open bigWig, bigBed and HiC files

```python
reader = gwseq_io.open(path, *, parallel, zoom_correction)
```

Parameters:
- `parallel` Number of parallel file handles and processing threads. 24 by default.
- `zoom_correction` Scaling factor for automatic zoom level selection based on bin size. Only for bigWig files. 1/3 by default.

Attributes for bigWig and bigBed files:
- `main_header` General file formatting info.
- `zoom_headers` Zooms levels info (reduction level and location).
- `auto_sql` BED entries declaration (only in bigBed).
- `total_summary` Statistical summary of entire file values (coverage, sums and extremes).
- `chr_sizes` Chromosomes IDs and sizes.
- `type` Either "bigwig" or "bigbed".

Attributes for HiC files:
- `header` `footer` General file info.
- `chr_sizes` Chromosomes IDs and sizes.
- `normalizations` Available normalizations.
- `units` Available units.
- `bin_sizes` Available bin sizes.

### Read bigWig and bigBed signal

```python
values = reader.read_signal(chr_ids, starts, ends)
values = reader.read_signal(chr_ids, starts=starts, span=span)
values = reader.read_signal(chr_ids, ends=ends, span=span)
values = reader.read_signal(chr_ids, centers=centers, span=span)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` Chromosomes ids, starts, ends and centers of locations. Both `starts` `ends` or one of `starts` `ends` `centers` (with `span`) may be specified.
- `span` Reading window in bp relative to locations `starts` `ends` `centers`. Only one reference may be specified if specified. Not by default.
- `bin_size` Reading bin size in bp. May vary in output if locations have variable spans or `bin_count` is specified. 1 by default.
- `bin_count` Output bin count. Inferred as max location span / bin size by default.
- `bin_mode` Method to aggregate bin values. Either "mean", "sum" or "count". "mean" by default.
- `full_bin` Extend locations ends to overlapping bins if true. Not by default.
- `def_value` Default value to use when no data overlap a bin. 0 by default.
- `zoom` BigWig zoom level to use. Use full data if -1. Auto-detect the best level if 0 by selecting the larger level whose bin size is lower than the third of `bin_size` (may be the full data). Full data by default.
- `progress` Function called during data extraction. Takes the extracted coverage and the total coverage in bp as parameters. Use default callback function if true. None by default.

Returns a numpy float32 array of shape (locations, bin count).

### Quantify bigWig and bigBed signal

```python
values = reader.quantify(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` `span` `bin_size` `full_bin` `def_value` `zoom` `progress` Identical to `read_signal` method.
- `reduce` Method to aggregate values over span. Either "mean", "sd", "sem", "sum", "count", "min" or "max". "mean" by default.

Returns a numpy float32 array of shape (locations).

### Profile bigWig and bigBed signal

```python
values = reader.profile(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` `span` `bin_size` `bin_count` `bin_mode` `full_bin` `def_value` `zoom` `progress` Identical to `read_signal` method.
- `reduce` Method to aggregate values over locations. Either "mean", "sd", "sem", "sum", "count", "min" or "max". "mean" by default.

Returns a numpy float32 array of shape (bin count).

### Read bigBed entries

```python
values = reader.read_entries(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` `spans` `progress` Identical to `read_signal` method.

Returns a list (locations) of list of entries (dict with at least "chr", "start" and "end" keys).

### Convert bigWig to bedGraph or WIG

```python
reader.to_bedgraph(output_path)
reader.to_wig(output_path)
```

Parameters:
- `output_path` Path to output file.
- `chr_ids` Only extract data from these chromosomes. All by default.
- `zoom` Zoom level to use. Full data by default.
- `progress` Function called during data extraction. Takes the extracted coverage and the total coverage in bp as parameters. None by default.

### Convert bigBed to BED

```python
reader.to_bed(output_path)
```

Parameters:
- `output_path` `chr_ids` `progress` Identical to `to_bedgraph` and `to_wig` methods.
- `col_count` Only write this number of columns (eg, 3 for chr, start and end). All by default.

### Write bigWig file

```python
writer = bigwig_io.open(path, "w")
writer = bigwig_io.open(path, "w", def_value=0)
writer = bigwig_io.open(path, "w", chr_sizes={"chr1": 1234, "chr2": 1234})
writer.add_entry("chr1", start=1000, end=1010, value=0.1)
writer.add_value("chr1", start=1000, span=10, value=0.1)
writer.add_values("chr1", start=1000, span=10, values=[0.1, 0.1, 0.1, 0.1])
```
must be pooled by chr, and sorted by (1) start (2) end
no overlap

### Write bigBed file

```python
writer = bigwig_io.open(path, "w", type="bigbed")
writer = bigwig_io.open(path, "w", type="bigbed", chr_sizes={"chr1": 1234, "chr2": 1234})
writer = bigwig_io.open(path, "w", type="bigbed", fields=["chr", "start", "end", "name"])
writer = bigwig_io.open(path, "w", type="bigbed", fields={"chr": "string", "start", "uint", "end": "uint", "name": "string"})
writer.add_entry("chr1", start=1000, end=1010)
writer.add_entry("chr1", start=1000, end=1010, fields={"name": "read#1"})
```
must be pooled by chr, and sorted by (1) start (2) end
may be overlapping

### Read HiC signal

```python
values = reader.read_signal(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` Chromosomes ids, starts and ends of the 2 locations.
- `bin_size` Input bin size or -1 to use the smallest. Must be available in the file. Smallest by default.
- `bin_count` Approximate output bin count. Takes precedence over `bin_size` if specified by selecting the closest bin size resulting in `bin_count`. Not specified by default.
- `exact_bin_count` Resize output to match `bin_count` (if specified). Not by default.
- `full_bin` Extend locations ends to overlapping bins if true. Not by default.
- `def_value` Default value to use when no data overlap a bin. 0 by default.
- `triangle` Skip symmetrical data if true. Not by default.
- `min_distance` `max_distance` Min and max distance in bp from diagonal for contacts to be reported. All by default.
- `normalization` Either "none" or any normalization available in the file, such as "kr", "vc" or "vc_sqrt". "none" by default.
- `mode` Either "observed" or "oe" (observed/expected). "observed" by default.
- `unit` Either "bp" or "frag". "bp" by default.
- `save_to` Save output to this .npz path (under "values" key) and return nothing. Not by default.

Returns a numpy float32 array of shape (loc 1 bins, loc 2 bins).

### Read HiC sparse signal

```python
values = reader.read_sparse_signal(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `bin_size` `bin_count` `exact_bin_count` `full_bin` `def_value` `triangle` `min_distance` `max_distance` `normalization` `mode` `unit` `save_to` Identical to `read_signal` method.

Returns a COO sparse matrix as a dict with keys:
- `values` Values as a numpy float32 array.
- `row` Values rows indices as a numpy uint32 array.
- `col` Values columns indices as a numpy uint32 array.
- `shape` Shape of the dense array as a tuple.

Convert in python using `scipy.sparse.csr_array((x["values"], (x["row"], x["col"])), shape=x["shape"])`.
