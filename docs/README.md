# README
### Hi! Please see readme.log for example output.

### you may found some hard-code API_KEY in codes but don't worry the api is fully managed by myself and have a restriction.
### Feel free to use it!

work.pdf contains brief intro of out works'architecture and the results of the experiments.

## **TF-IDF Score Formula**
\[
\text{TF-IDF Score} = \sum_{i = 1}^{N} \text{TF-IDF}(w_{i})
\]

### **Definition of Variables**
- \( N \) = Total number of words in the document (tweet).  
- \( w_{i} \) = The \( i \)-th word in the document.  
- \( \text{TF-IDF}(w_{i}) \) = The TF-IDF score of word \( w_{i} \), calculated as:

\[
\text{TF-IDF}(w_{i}) = \text{TF}(w_{i}) \times \text{IDF}(w_{i})
\]

where:
- **Term Frequency (TF)**: The frequency of word \( w_{i} \) in the document:
  
  \[
  \text{TF}(w_{i}) = \frac{\text{Number of times } w_{i} \text{ appears in the document}}{\text{Total number of words in the document}}
  \]

- **Inverse Document Frequency (IDF)**: A measure of how unique the word is across the entire corpus:

  \[
  \text{IDF}(w_{i}) = \log \left(\frac{\text{Total number of documents}}{\text{Number of documents containing } w_{i}} + 1\right)
  \]

### **Interpretation**
- **Higher TF-IDF scores** indicate that a word is **important** in the document (tweet) but **not common** across all documents.
- Words that appear **frequently** in one document but **rarely** in others will have **higher importance scores**.

## **Normalize Engagement Metrics**

Each engagement metric is normalized using **Min-Max Scaling with 95th Percentile Clipping**:

### **1. Normalized Reply Count**
\[
\text{Norm Reply} = \frac{\min(\text{tweet_reply_count}, Q_{95}^{\text{reply}}) - \min(\text{tweet_reply_count})}{Q_{95}^{\text{reply}} - \min(\text{tweet_reply_count}) + 1e^{-8}}
\]

### **2. Normalized Quote Count**
\[
\text{Norm Quote} = \frac{\min(\text{tweet_quote_count}, Q_{95}^{\text{quote}}) - \min(\text{tweet_quote_count})}{Q_{95}^{\text{quote}} - \min(\text{tweet_quote_count}) + 1e^{-8}}
\]

### **3. Normalized Conflict Ratio**
\[
\text{Conflict Ratio} = \frac{\text{tweet_reply_count} + \text{tweet_quote_count}}{\text{tweet_like_count} + \text{tweet_retweet_count} + 1}
\]

\[
\text{Norm Ratio} = \frac{\min(\text{Conflict Ratio}, Q_{95}^{\text{ratio}}) - \min(\text{Conflict Ratio})}{Q_{95}^{\text{ratio}} - \min(\text{Conflict Ratio}) + 1e^{-8}}
\]

### **Explanation of Variables**
- \( Q_{95}^{\text{reply}}, Q_{95}^{\text{quote}}, Q_{95}^{\text{ratio}} \) = **95th percentile values** for each metric.
- **Clipping** ensures outliers don’t dominate the scores.
- \( 1e^{-8} \) prevents division by zero.

### **Interpretation**
- Each metric is **scaled between 0 and 1**.
- Values are **adjusted to reduce the impact of outliers**.
- Higher values indicate **greater engagement relative to the dataset**.

## **Compute Engagement Score**

The **Engagement Score** is calculated as the sum of various engagement metrics:

\[
E = \text{tweet_reply_count} + \text{tweet_retweet_count} + \text{tweet_like_count} + \text{tweet_quote_count} + \text{tweet_bookmark_count}
\]

### **Explanation of Variables**
- \( E \) = **Engagement Score** (total interactions on a tweet).
- \( \text{tweet_reply_count} \) = Number of replies to the tweet.
- \( \text{tweet_retweet_count} \) = Number of retweets.
- \( \text{tweet_like_count} \) = Number of likes.
- \( \text{tweet_quote_count} \) = Number of quote tweets.
- \( \text{tweet_bookmark_count} \) = Number of times the tweet was bookmarked.

### **Interpretation**
- Higher engagement scores indicate **higher user interaction** with the tweet.
- The score considers **all forms of engagement**, not just likes or retweets.
- **Tweets with high engagement scores** are more likely to be **influential or viral**.

## **Compute Raw Importance Score**

The **raw importance score** is calculated as the product of the **TF-IDF Score** and the **Engagement Score**:

\[
\text{Importance Score} = \text{TF-IDF Score} \times \text{Engagement Score}
\]

### **Explanation of Variables**
- \( \text{Importance Score} \) = The raw measure of a tweet’s importance.
- \( \text{TF-IDF Score} \) = The importance of words in the tweet based on **Term Frequency-Inverse Document Frequency (TF-IDF)**:
  
  \[
  \text{TF-IDF Score} = \sum_{i=1}^{N} \text{TF-IDF}(w_i)
  \]

  where:
  - \( N \) = Total number of words in the tweet.
  - \( w_i \) = The \( i \)-th word in the tweet.
  - \( \text{TF-IDF}(w_i) \) = The TF-IDF value of word \( w_i \).

- \( \text{Engagement Score} \) = The total interaction with a tweet:

  \[
  E = \text{tweet_reply_count} + \text{tweet_retweet_count} + \text{tweet_like_count} + \text{tweet_quote_count} + \text{tweet_bookmark_count}
  \]

### **Interpretation**
- The **TF-IDF Score** captures **textual importance** based on how unique and relevant the words are.
- The **Engagement Score** captures **user interaction** with the tweet.
- **Multiplication** ensures that **only highly engaged tweets with important textual content** receive **higher importance scores**.
- This raw score will later be **normalized** to a **0-100 scale** for better interpretability.