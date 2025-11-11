mds-cashbook
============
Tryton module to add a cashbook.

Install
=======

pip install mds-cashbook

Requires
========
- Tryton 6.0

How to
======

This module adds a cash book to Tryton. Each Tryton user can have
any number of cash books. The cash books can be arranged hierarchically.
A cash book contains simple postings, such as expense, revenue, transfer,
split posting. Each booking has a category, an amount and possibly a description.
The cash books of the different Tryton users are separated from
each other by permissions. There is an enhancement module for the connection
to the chart of accounts and analytic.

This module adds new user groups:

Cashbook
    The user can make entries in his cash books.

Cashbook - WF - Check
    The user can mark his bookings as 'checked'

Cashbook - WF - Done
    The user can reconcile his cash books

Cashbook - Administrator
    the Cashbook-Administrator

There is a possibility to allow reading or editing for other users via
the Tryton user groups. This makes it possible to set up a administrator
for all cash books of the Tryton system.


Set up your cash book
---------------------

Add the Tryton user to the *Cashbook* group. In the tab *Owner and Authorizeds*,
enter the user as the owner. Enter *Type*, *Currency*, *Initial Date*
and *Line Numbering*. Cash books without a type cannot receive postings
and are treated as a view. You can create several cash books per user
and arrange them hierarchically.


Creating categories
-------------------

Each booking needs a category. The categories are separated by revenue and expense.
In the menu Cash Book / Configuration / Category you create some categories.


Using the chart of accounts
---------------------------

If you want to have the postings as a posting record in Tryton Accounting
install the *cashbook_account* module. For analytic, install *cashbook_analytic*.
In each of the cash books, add one account to the
chart of accounts, in tab *Account Configuration*.

In the categories you add a chart of accounts account in the
tab 'Account and Tax'. If you want to make your transactions with taxes,
you can also add one or more taxes.

Enter bookings
--------------

There are two ways to enter bookings.

1) The *Enter Booking* wizard. The wizard is optimized for use on
   small screens. You can write down expenses on the go with your smartphone.
   The type of bookings is limited to expense, revenue and transfers between cash books.
   When using the wizard, you should check the booking later and possibly complete it.

2) The record form of a cash book. This option offers all posting variants,
   such as expense, revenue, transfer to, transfer from, expense split posting
   and revenue split posting. When using chart of accounts and analytic,
   you also specify the taxes and analytic accounts here.


Processing states
-----------------

Postings in cash books have several workflow states.

Edit
    The entry has been created but not yet verified

Checked
    The user has checked his entry and has indicated this by clicking on 'Check'
    When using the chart of accounts modules, posting records are created here
    in the Draft state.

Reconciled
    A user (with enough permissions) has checked the entry against a
    bank statement. This step is performed in the 'Reconciliations' tab of a cash book.

Done
    The entry is committed. This step is performed by completing a
    reconciliation in the cash book. When using the chart of accounts modules,
    the posting records created in step 'Check' are committed.


Reconciliation
--------------

The bookings should be checked regularly against a bank statement. This is done
in the 'Reconciliations' tab of a cash book.

1) Click the plus button, don't change anything about the contents,
   click *ok*, save the cash book. The system will change the dates of the
   reconciliation so that all eligible bookings are taken into account.

2) If you want to change the end date, do so now. Save.

3) Open the reconciliation by double-clicking, click on *Check*.
   This will insert all posting lines into the list. The posting lines
   in the cash book are now protected against edit.

4) Now check line by line against an account statement. To remember what you
   have already seen, click the 'Reconciled' button.

5) When you're done, click the *Done* button of the reconciliation. This
   sets all posting lines and the reconciliation to *Done*.


Configuration
-------------

The configuration in the menu Cash Book / Configuration is a user-specific setting.
The user can choose which cash books appear in the *Enter Booking* dialog and
which default settings should apply when opening a cash book.


Foreign currencies
------------------

The cash books can be used with foreign currency. Base currency is the company currency.
For transfers between cash books with different currencies, the current conversion
rate in Tryton is used. You can adjust the exchange rate actually used in the booking dialog.
If you have hierarchical cash books, the amounts of subordinate cash books with foreign
currency are converted  into the display currency of the parent cash book.


Changes
=======

*6.0.38 - 10.11.2025*

- configuration: rename field 'fixate' to 'check booking'

*6.0.37 - 21.10.2025*

- add: date-field to booking-wizard

*6.0.35 - 01.06.2024*

- add: config setting for fixate in booking-wizard

*6.0.34 - 30.05.2024*

- add: fixate of booking from booking-wizard

*6.0.33 - 31.12.2023*

- remove caching
- add worker-based precalculation of cashbook-values

*6.0.31 - 30.11.2023*

- optimized ir.rule

*6.0.30 - 25.07.2023*

- updt: optimize code, add tests

*6.0.28 - 05.06.2023*

- code optimized

*6.0.27 - 05.03.2023*

- updt: optimize caching
- add: settings for trytond.conf

*6.0.26 - 27.02.2023*

- updt: cashbook-form optimized
- add: caching

*6.0.25 - 14.02.2023*

- fix: possible exception by invalid date in context
- updt: optimize table + icon

*6.0.24 - 05.02.2023*

- fix: rewrite of line-values

*6.0.23 - 28.01.2023*

- fix: selection of subordinate cash books for calculations

*6.0.22 - 21.01.2023*

- add: enable extension by investment-module
- updt: optimize form/list-views

*6.0.21 - 29.11.2022*

- updt: remove 'reconcile' button from line-form
- add: how to

*6.0.20 - 16.11.2022*

- add: new state 'reconciled' at line

*6.0.19 - 19.10.2022*

- fix: delete()

*6.0.18 - 11.10.2022*

- updt: optimized open/view of cashbook

*6.0.17 - 10.10.2022*

- add: colors for cashbook-lines
- add: client stores tree-state of cashbook

*6.0.16 - 07.10.2022*

- add: open cashbook-lines from cashbook

*6.0.15 - 04.10.2022*

- updt: second-currency support optimized

*6.0.14 - 30.09.2022*

- fix: parameter

*6.0.13 - 28.09.2022*

- hierarchical ordering for cashbook
- forms optimzed

*6.0.12 - 18.09.2022*

- add: selected cashbooks in 'enter-booking-dialog'

*6.0.11 - 16.09.2022*

- add: hierarchy for cashbooks

*6.0.10 - 13.09.2022*

- add: split-booking with transfer

*6.0.9 - 08.09.2022*

- updt: allow negative amounts

*6.0.8 - 07.09.2022*

- updt: enter-booking form optimized

*6.0.7 - 07.09.2022*

- add: enter-booking-wizard

*6.0.6 - 06.09.2022*

- updt: optimized form - line, line-context
- updt: extended search in cashbook-lines

*6.0.5 - 05.09.2022*

- updt: view of book + line optimized

*6.0.4 - 05.09.2022*

- fix: write number at state-change 'check' -> 'done'
- updt: speedup transaction view

*6.0.3 - 31.08.2022*

- updt: checks, sorting

*6.0.2 - 25.08.2022*

- add: split-booking

*6.0.1 - 23.08.2022*

- works

*6.0.0 - 05.08.2022*

- init
