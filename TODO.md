## For the channel loader

- [x] collect fwd from id, title
- [x] collect fwd from name handle
- [ ] add mentions
- [x] try and get entities from the message itself to avoid reaching the limit (or use asincio await)
- [x] do some refactoring (with handler function)
- [x] set variable source for channels list 

## For the network analysis

- [ ] compiling the motivated list of seed channels
- [ ] building the weighted directed graph (calculate betweenness?)
- [ ] visualize with https://cytoscape.org/?
- [ ] take a closer look at http://networksciencebook.com/, https://global.oup.com/academic/product/networks-9780198805090
- [ ] explore https://networkx.org/, https://github.com/swamiiyer/robustness (for betweenness)
- [ ] collect 3? cascades of references, estimate the spread
- [ ] distill the research data on main algos for maximizing the influence
- [ ] implement and finalize the dataset
