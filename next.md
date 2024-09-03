# General

- Is stock table necessary? Can't we just look up by ticker?
  - Not extendable, can't get deeper stock info
  - Ok then how to dynamically create new stock record
    - Need db to be relational to detect error on null stock so we can handle the error
    - (This avoids checking if a stock exists every time? (If there is error handling for sql insertions))

# ToDo

## Scraper

## Database

- Maybe switch from cockroach if it is still slow
  - If so swap to planetscale or something and bite bullet with payment
- Calculate storage size for 6 months of records
-

## API

- Not flask cuz that was annoying to hostl

## Front End
