# Refractoring Process for Webshop Application

We employ Martin Fowler's TDD
![Image](https://i.ibb.co/sPpWtp2/Screenshot-2023-04-27-at-20-40-38.png)

Detailed approach can be found in the [Wiki pages](https://github.com/kayesokua/webshop/wiki/Refactoring-Approach)

## Focus of Refractoring

The `checkout()` function found in `./application/orders/routes.py`

Commit can be found [here](https://github.com/kayesokua/webshop/commit/7831075080149cde7a197c9c30194b726709eb15).

### Static Code Analysis

We used flake8 to analysise the file and made the necessary changes. Screenshot below:
![Image](./flake8_suggestion_orders.png)

### Code Smells We Identified and Solutions We Applied

- [x] Long Method/Function: Separate the main function into smaller helper functions, each with a specific purpose
- [x] Misleading Name: Use more descriptive function and variable names
- [x] Dispensables: Remove unnecessary print statements and comments
- [ ] There are magic numbers in the code(ie. fixed shipping rates) - due to third integration usage, further look into this will be needed.
