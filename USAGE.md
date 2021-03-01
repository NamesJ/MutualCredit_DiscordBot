# Usage guide


## Membership
The bot will only accept commands from users with the `member` role, which prevents non-`member`s from using the bot.


## Creating an account
```
!create_account
```
The first command every member must run.
You will not be able to run any commands (except `!help`) until you create an account.


## Check your account balance, available balance, and pending balance
```
!balance
```


## Check your allowed account balance range
```
!show_range
```


## Creating a new offer
```
# Create an offer without categories
!create_offer TITLE PRICE DESCRIPTION

#Create an offer with categories (optional)
!create_offer TITLE PRICE DESCRIPTION CATEGORY_1 CATEGORY_2 CATEGORY_3 ...
```


## Deleting an old offer
```
# Deleting a single offer
!delete_offers OFFER_ID

# Deleting multiple offers
!delete_offers OFFER_ID_1 OFFER_ID_2 OFFER_ID_3 ...
```


## List offers by member
```
!list_offers @USER
```
`@USER` should be a *mention* to another user.
A more convenient way of listing your own offers is `!list_offers` without any arguments.


## List the categories associated with an offer
```
!list_categories OFFER_ID
```


## Add categories to an offer (your own)
```
!add_categories OFFER_ID CATEGORY_1 CATEGORY_2 CATEGORY_3 ...
```


## Remove categories to an offer (your own)
```
!remove_categories OFFER_ID CATEGORY_1 CATEGORY_2 CATEGORY_3 ...
```


## Sending a buy request
```
# Sending a single buy request
!buy OFFER_ID

# Sending multiple buy requests
!buy OFFER_ID_1 OFFER_ID_2 OFFER_ID_3 ...
```


## Cancelling a pending buy request
```
# Cancelling a single pending buy request
!cancel TRANSACTION_ID

# Cancelling multiple pending buy requests
!cancel TRANSACTION_ID_1 TRANSACTION_ID_2 TRANSACTION_ID_3 ...
```


## Denying a received buy request
```
# Denying a single buy request
!deny TRANSACTION_ID

# Denying multiple buy requests
!deny TRANSACTION_ID_1 TRANSACTION_ID_2 TRANSACTION_ID_3 ...
```


## Approving a received buy request
```
# Approving a single buy request
!approve TRANSACTION_ID

# Approving multiple buy requests
!approve TRANSACTION_ID_1 TRANSACTION_ID_2 TRANSACTION_ID_3 ...
```
