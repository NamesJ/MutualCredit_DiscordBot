# Usage guide


## Membership
The bot will only accept commands from users with the `member` role, which prevents non-`member`s from using the bot.


## A note on where you can run commands

### Public channels ONLY
- `!offer show` *(for another member's account)*

### Public channels OR Private DM channel with bot
- `!account allowance`
- `!account balance`
- `!account create`
- `!category add`
- `!category remove`
- `!category show`
- `!offer add`
- `!offer remove`
- `!offer show` *(for your own account)*
- `!transaction approve`
- `!transaction cancel`
- `!transaction deny`
- `!transaction request`
- `!help`
- `!kill`



**Create an account**
*You must run this command first to use any of the commands below*
`!account create`

**Check your allowance (max debit/credit)**
`!account allowance`

**Check your balance**
*Returns account balance, available balance (balance - pending transfer requests sent from you) and pending sales (pending transfer requests sent to you) for your offers)*
`!account balance`

**Add one or more categories to an offer**
`!category add OFFER_ID CATEGORY [CATEGORY ...]`

**Remote one or more categories from an offer**
`!category remove OFFER_ID CATEGORY [CATEGORY ...]`

**Create a new offer (optionally with one or more categories)**
`!offer add TITLE PRICE DESCRIPTION [CATEGORY CATEGORY ...]`

**Remove one or more of your offers**
`!offer remove OFFER_ID [OFFER_ID OFFER_ID]`

**Show offers from an account**
*`@USER` indicates that your should use a `mention` ('@' someone)*
`!offer show @USER`

**Approve a transfer request from someone**
*The buyer(s) will be notified that you have denied their request(s)*
*If successful, the offer price(s) will be added to your balance*
`!transaction approve TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Cancel one or more of your pending transfer requests**
*The seller(s) will be notified that your request(s) have been cancelled*
`!transaction cancel TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Deny a transfer request from someone**
*The buyer(s) will be notified that you have denied their request(s)*
`!transaction deny TRANSACTION_ID [TRANSACTION_ID TRANSACTION_ID...]`

**Create a transfer request for one or more offers**
*The seller(s) will be notified of your request(s)*
`!transaction request OFFER_ID [OFFER_ID OFFER_ID ...]`


## Creating an account
```
!account create
```
The first command every member must run.
You will not be able to run any commands (except `!help`) until you create an account.


## Check your account balance, available balance, and pending balance
```
!account balance
```


## Check your account's allowance (minimum/maximum allowed balance)
```
!account allowance
```


## Show a member's offers
```
!offer show @USER
```
`@USER` should be a *mention* to another user.
A more convenient way of listing your own offers is `!offer show` without any additional arguments.
*Note: This command can only be used in a public channel as the mention suggestion system does not work in private DM with bot.*


## Creating a new offer
```
# Create an offer without categories
!offer add TITLE PRICE DESCRIPTION

#Create an offer with categories (optional)
!offer add TITLE PRICE DESCRIPTION CATEGORY_1 CATEGORY_2 CATEGORY_3 ...
```


## Deleting an old offer
```
# Deleting a single offer
!offer remove OFFER_ID

# Deleting multiple offers
!offer remove OFFER_ID_1 OFFER_ID_2 OFFER_ID_3 ...
```


## List the categories associated with an offer
```
!category show OFFER_ID
```


## Add category/categories to your offer
```
!category add OFFER_ID CATEGORY_1 CATEGORY_2 CATEGORY_3 ...
```


## Remove category/categories from one of your offers
```
!category remove OFFER_ID CATEGORY_1 CATEGORY_2 CATEGORY_3 ...
```


## Send transaction request(s) for one or more offers (of one or more sellers)
*You will only be allowed to create a transfer request if your balance will not exceed it's allowance*
*Seller(s) will be notified of your transaction request*
```
# Sending a single buy request
!transaction request OFFER_ID

# Sending multiple buy requests
!transaction request OFFER_ID_1 OFFER_ID_2 OFFER_ID_3 ...
```


## Canceling a transaction request you previously sent
*A transaction can only be canceled if it is still pending*
*Seller will be notified of you having canceled the request*
```
# Cancelling a single pending buy request
!transaction cancel TRANSACTION_ID

# Cancelling multiple pending buy requests
!cancel TRANSACTION_ID_1 TRANSACTION_ID_2 TRANSACTION_ID_3 ...
```


## Denying a received buy request
*A transaction can only be canceled if it is still pending*
*Buyer will be notified of you having denied the request*
```
# Denying a single buy request
!transaction deny TRANSACTION_ID

# Denying multiple buy requests
!transaction deny TRANSACTION_ID_1 TRANSACTION_ID_2 TRANSACTION_ID_3 ...
```


## Approving a received buy request
*A transaction can only be canceled if it is still pending*
*Buyer will be notified of you having denied the request*
*You will only be allowed to approve a transfer request if your balance will not exceed it's allowance*
```
# Approving a single buy request
!transaction approve TRANSACTION_ID

# Approving multiple buy requests
!transaction approve TRANSACTION_ID_1 TRANSACTION_ID_2 TRANSACTION_ID_3 ...
```
