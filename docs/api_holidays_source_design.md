# API Holidays Source Design

## Purpose

This document defines the design for adding a public holiday/calendar API source to the Retail Analytics Data Platform.

The goal is to enrich order, revenue, delivery, and review analysis with calendar context.

This source is not a replacement for the main transactional source.  
It is an enrichment source.

---
## Source Type

External REST API.

---

## Selected API

The selected API is:

`Nager.Date Public Holiday API`

Endpoint pattern:

```text
GET https://date.nager.at/api/v3/publicholidays/{year}/{country_code}

Initial project endpoint:

https://date.nager.at/api/v3/PublicHolidays/2016/BR
https://date.nager.at/api/v3/PublicHolidays/2017/BR
https://date.nager.at/api/v3/PublicHolidays/2018/BR

## Business Purpose

The holiday source supports business questions such as:

- Do order volumes change around public holidays?
- Do revenue patterns change around holiday periods?
- Do delivery delays increase around public holidays?
- Do review scores change around holiday periods?
- Should BI dashboards distinguish normal days from public holidays?
