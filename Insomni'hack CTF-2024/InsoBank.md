---
title: Insomni'hack CTF-Writeup
date: 2024-01-21 17:24:33
tags:

---

# InsoBank

The web application in this challenge is a banking app that supports transferring deposits from one account to another. However, all the accounts involved in a transfer operation must belong to the same person; this means we cannot transfer money from our account to other people’s accounts.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-3efa36c075e76cd8aa3544262dd2e6f9.png)

Through the registration functionality, we can create new accounts. Every new account starts with a $10 initial deposit in the `current account`, and has empty `saving account` and `checking account`.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-483ce216483887f34f0c02b4d9235e17.png)

To obtain the flag, we must have one account with more than $10 in deposits. However, transferring exactly $10 around is pointless. How do we unexpectedly increase the amount?

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-695a7ba5b906152e93f752ce3c8f38ae.png)

After a thorough code review, here are the vulnerabilities that we can exploit:

1. **Discrepancies in Data Precision**

There are differences in the data precision of the `amount` field between two `batch_transactions` tables.

In the MySQL database, the data type of `amount` is ****`decimal(10,2)`, while in the PostgreSQL database, it is just `decimal`. This causes a floating-point number like 0.014 to be stored in MySQL as 0.01, but as 0.014 in PostgreSQL.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-09a3c70cf6a9e46ab257bb8aa97644a1.png)

1. **Logic Flaws**

The transaction process allows a user to set up a request to transfer a certain amount of money from one account to another. If the account has enough funds, the transaction is marked as validated, and the amount being transferred is deducted.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-a180062200d3fe70aa3d2163220a7ea3.png)

Based on the `batch_id`, the server-side periodically operates transfer requests in batches via a cron job named `exec_transfers.py`. This job sums up the total number of transactions with the same `batch_id` and adds that number to the recipient’s account.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-75a08428ba4bfea9846a366ef70b8f7f.png)

The logic flaw arises here. The amount to deduct is based on `decimal(10,2)`, while the amount to increase is based on `decimal`. When two transactions with the same `batch_id` are processed at once, an extra $0.01 gets smuggled into the recipient’s account.

For example, if two transactions are each transferring $0.014 from saving to checking account, the sender’s account gets deducted by $0.02, but the recipient’s account gets increased by $0.028, which rounds up to $0.03.

1. **Race condition**

Now that we have a clear approach to siphoning money from thin air, there's one thing I haven’t mentioned: the application actually doesn’t allow two transfers per recipient in a batch.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-d42b9be70034246dc5b4e53ce181a306.png)

However, we can achieve this by exploiting a race condition, as there is no lock when looking up the table to check for redundant transfers.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-027d9c74f61b33cef776fe300f9e4b1d.png)

Here, I use Turbo Intruder, a plugin of Burp Suite, to concurrently send two requests.

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-9f33ff8aa8a4fdc984173bdbcf09f209.png)

Things are going well!

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-71e8457250a41188d16dd6c522f04927.png)

And I’m definitely on my way to becoming a billionaire!

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-261bbd7347784f3c6373c08883911a5c.png)

# Flag

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/17-27-55-a44fdbbeba7fc96c99cfbfd85661fec2.png)
