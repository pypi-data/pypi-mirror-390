from colorama import Fore, Style, init

init(autoreset=True)

def amt_1():
    print(Fore.RED + '''

#Data Preprocessing

import pandas as pd

df = pd.read_csv('data.csv')

#Dropping the irrelevant columns
columns_to_drop = [
    'col_name',
]

df = df.drop(columns=columns_to_drop)
print(df.columns)

#Checking the null values and removing them
print(df.isnull().sum())
df = df[df['comment_text'].notna()]
df = df[df['language'].notna()]
print(df.isnull().sum())

#Box plot to check for outliers
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 4))
plt.boxplot(df['like_count'], vert=False)
plt.title('Boxplot of Like Count')
plt.xlabel('Like Count')
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 4))
plt.boxplot(df['like_count'], vert=False)
plt.title('Boxplot of Reply Count')
plt.xlabel('Reply Count')
plt.grid(True)
plt.show()


#Removing the outliers
df = df[df['like_count'] <= 5000]
df = df[df['reply_count'] <= 500]
print("Remaining rows:", df.shape[0])

#Filtering and removing the values other than spam and not spam
df = df[df['label_spam'].isin(['spam', 'not spam'])] 
df['spam_label'] = df['label_spam'].map({'not spam': 0, 'spam': 1})


heatmap_data = df[['like_count', 'reply_count', 'spam_label']]

correlation = heatmap_data.corr()

plt.figure(figsize=(6, 4))
plt.imshow(correlation, cmap='coolwarm')
plt.colorbar()

plt.xticks(range(len(correlation.columns)), correlation.columns)
plt.yticks(range(len(correlation.columns)), correlation.columns)

plt.title("Correlation Heatmap")
plt.tight_layout()
plt.show()
        
          ''')

def amt_2():
    print(Fore.RED + '''

#EDA

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import re

df = pd.read_csv('anime_data.csv')

#Clean airing date, duration and demographic
df['Aired_from'] = df['Aired'].str.extract(r'^(.*) to')[0]
df['Aired_from'] = pd.to_datetime(df['Aired_from'])

df['Duration_min'] = df['Duration'].str.extract(r'(\d+)').astype(float)

df['Demographic'] = df['Demographic'].str.replace(r'(\w+)\1', r'\1', regex=True)

# Extract broadcast day
df['Broadcast_Day'] = df['Broadcast'].str.extract(r'(\w+days?)')
# Extract time (e.g., "23:00")
df['Broadcast_Time'] = df['Broadcast'].str.extract(r'(\d{2}:\d{2})')

# Fix repeated genre words
def clean_genres(text):
   if pd.isna(text):
       return text
   return re.sub(r'(\w+)\1', r'\1', text)

# Apply the function to the 'Genres' column
df['Genres'] = df['Genres'].apply(clean_genres)


df['Genres'] = df['Genres'].str.split(', ')
df['Producers'] = df['Producers'].str.split(', ')
df['Studios'] = df['Studios'].str.split(', ')

df['Rating'] = df['Rating'].str.extract(r'^(.*?)(?:\s*-|$)')[0].str.strip()

df = df[df['Episodes'] != 'Unknown']
df['Episodes'] = df['Episodes'].astype(int)

columns_to_drop = ['Column Name', ]
df = df.drop(columns=columns_to_drop)

df.head()
          

#Mean, Median & Mode:
columns_to_analyze = ['Score', 'Rank', 'Episodes', "Duration_min"]
desc_stats = df[columns_to_analyze].agg(['mean', 'median'])
mode_stats = df[columns_to_analyze].mode().iloc[0]

print(desc_stats)
print(mode_stats)

for col in columns_to_analyze:

   mean = df[col].mean()
   median = df[col].median()
   if abs(mean - median) < 1:
       print(f"{col}: Symmetric (mean ≈ median)")
   elif mean > median:
       print(f"{col}: Right-skewed (mean > median)")
   else:
       print(f"{col}: Left-skewed (mean < median)")


#Bar & Stacked Bar Plot:

sns.countplot(x='Type', data=df)
plt.title("Anime Count by Type")
plt.show()

pd.crosstab(df['Demographic'], df['Rating']).plot(kind='bar', stacked=True)
plt.title("Stacked Bar: Demographic vs Rating")
plt.ylabel("Count")
plt.show()


#Histogram

# plt.figure(figsize=(30, 15))
sns.histplot(df['Type'], bins=20 )
plt.title("Distribution of Episodes")
plt.show()

#Scatter Plot

sns.scatterplot(x='Score', y='Popularity', hue='Type', data=df)
plt.title("Score vs Popularity by Type")
plt.show()

#Boxplot

sns.boxplot(x='Broadcast_Day', y='Score', data=df)
plt.title("Score by Broadcast Day")
plt.show()


#Line Chart

df['Year'] = pd.to_datetime(df['Aired_from']).dt.year
df['Year'].value_counts().sort_index().plot(kind='line')
plt.title("Anime Releases Over Time")
plt.xlabel("Year")
plt.ylabel("Number of Anime")
plt.show()


#Violin

sns.violinplot(x='Rating', y='Episodes', data=df)
plt.title("Episodes by Rating")
plt.show()

#Swarm

sns.swarmplot(x='Type', y='Score', data=df)
plt.title("Score Distribution by Type")
plt.show()

#Donut

source_counts = df['Source'].value_counts()
plt.pie(source_counts, labels=source_counts.index, autopct='%1.1f%%', startangle=140, wedgeprops={'width':0.4})
plt.title("Donut Chart: Anime by Source")
plt.show()


#3D Scatter Plot

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(df['Score'], df['Popularity'], df['Rank'], c='skyblue', s=50)
ax.set_xlabel('Score')
ax.set_ylabel('Popularity')
ax.set_zlabel('Episodes')
plt.title("3D Scatter: Score vs Popularity vs Episodes")
plt.show()

#Heatmap

num_cols = ['Score', 'Popularity', 'Rank', 'Episodes', 'Duration_min']
corr = df[num_cols].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title("Correlation Heatmap")
plt.show()

          ''')
    
def amt_3():
    print(Fore.RED + '''
          
#Classification

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("bestSelling_games.csv")
print(df.head())


columns_to_drop = [
    'game_name', 'release_date', 'developer', 'user_defined_tags',
    'supported_os', 'supported_languages', 'other_features'
]

df = df.drop(columns=columns_to_drop)
print("Remaining columns:")
print(df.columns.tolist())
print("\nDataset shape after dropping columns:", df.shape)



print("Missing values per column:")
print(df.isnull().sum())
print("\nData types:")
print(df.dtypes)

df = df.dropna(subset=['reviews_like_rate', 'all_reviews_number', 'price', 'rating'])
print(f"\nDataset shape after removing missing values: {df.shape}")



plt.figure(figsize=(8, 4))
plt.boxplot(df['reviews_like_rate'], vert=False)
plt.title('Boxplot of Reviews Like Rate')
plt.xlabel('Reviews Like Rate')
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 4))
plt.boxplot(df['all_reviews_number'], vert=False)
plt.title('Boxplot of All Reviews Number')
plt.xlabel('All Reviews Number')
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 4))
plt.boxplot(df['price'], vert=False)
plt.title('Boxplot of Price')
plt.xlabel('Price')
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 4))
plt.boxplot(df['rating'], vert=False)
plt.title('Boxplot of Rating')
plt.xlabel('Rating')
plt.grid(True)
plt.show()


df = df[df['all_reviews_number'] <= 100000]  
df = df[df['price'] <= 100]
print("Remaining rows after outlier removal:", df.shape[0])




from sklearn.preprocessing import StandardScaler

# Scale numerical features
scaler = StandardScaler()

numerical_features = ['reviews_like_rate', 'all_reviews_number', 'price', 'difficulty', 'length', 'estimated_downloads']
scaled_features = scaler.fit_transform(df[numerical_features])

# Create scaled dataframe
scaled_df = pd.DataFrame(
    scaled_features,
    columns=[f'scaled_{col}' for col in numerical_features],
    index=df.index 
)

df = pd.concat([df, scaled_df], axis=1)
print("Scaled features added to dataset")
print("New columns:", [col for col in df.columns if 'scaled_' in col])



df['high_rated'] = (df['rating'] >= 3.3).astype(int)

# Display distribution of target variable
print("Distribution of target variable:")
print(df['high_rated'].value_counts())
print("\nPercentage distribution:")
print(df['high_rated'].value_counts(normalize=True) * 100)





# Create correlation heatmap
heatmap_features = ['scaled_reviews_like_rate', 'scaled_all_reviews_number', 'scaled_price', 'scaled_difficulty', 'scaled_length', 'high_rated']
heatmap_data = df[heatmap_features]
correlation = heatmap_data.corr()

plt.figure(figsize=(8, 6))
plt.imshow(correlation, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar()

plt.xticks(range(len(correlation.columns)), correlation.columns, rotation=45)
plt.yticks(range(len(correlation.columns)), correlation.columns)

plt.title("Correlation Heatmap")
plt.tight_layout()
plt.show()



#Train test split

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

X = df[['scaled_reviews_like_rate', 'scaled_all_reviews_number', 'scaled_price', 'scaled_difficulty', 'scaled_length', 'scaled_estimated_downloads', 'age_restriction']]
y = df['high_rated']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)



#Logistic Regression

from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\nLogistic Regression Classification Report:")
print(classification_report(y_test, y_pred))


#Decision Tree

from sklearn.tree import DecisionTreeClassifier

# Apply Decision Tree model
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)

y_pred = dt_model.predict(X_test)

print("\nDecision Tree Classification Report:")
print(classification_report(y_test, y_pred))




#Gaussian Naive Bayes

from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report

# Apply Gaussian Naive Bayes model
nb_model = GaussianNB()
nb_model.fit(X_train, y_train)

y_pred = nb_model.predict(X_test)

print("\nNaive Bayes (Gaussian) Classification Report:")
print(classification_report(y_test, y_pred))




#SVC

from sklearn.svm import SVC
from sklearn.metrics import classification_report

# Apply Support Vector Classifier model
svc_model = SVC(kernel='linear', random_state=42)
svc_model.fit(X_train, y_train)

y_pred = svc_model.predict(X_test)

print("\nSupport Vector Classifier Report:")
print(classification_report(y_test, y_pred))




#Random Forest

from sklearn.ensemble import RandomForestClassifier

# Apply Random Forest model
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)

print("\nRandom Forest Classification Report:")
print(classification_report(y_test, y_pred))




#PCA

from sklearn.decomposition import PCA
from sklearn.metrics import classification_report

pca = PCA(n_components=5)
X_train_pca = pca.fit_transform(X_train)
X_test_pca = pca.transform(X_test)

pca_model = LogisticRegression(random_state=42)
pca_model.fit(X_train_pca, y_train)

y_pred = pca_model.predict(X_test_pca)

print(classification_report(y_test, y_pred))




#ROC Curve

from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt

# Apply Logistic Regression for ROC analysis
roc_model = LogisticRegression(random_state=42)
roc_model.fit(X_train, y_train)
y_pred_proba = roc_model.predict_proba(X_test)[:, 1]

# Calculate ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
auc_score = roc_auc_score(y_test, y_pred_proba)

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr)
plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.grid(True)
plt.show()

print(f"\nROC AUC Score: {auc_score:.3f}")




#Bagging

from sklearn.ensemble import BaggingClassifier
from sklearn.metrics import classification_report

# Apply Bagging Classifier
bagging_model = BaggingClassifier(random_state=42, n_estimators=100)
bagging_model.fit(X_train, y_train)

y_pred = bagging_model.predict(X_test)

print("\nBagging Classifier Classification Report:")
print(classification_report(y_test, y_pred))




#Boosting - Ada boosting and Gradient Boosting

from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report

# Apply AdaBoost Classifier
boosting_model = AdaBoostClassifier(random_state=42, n_estimators=100)
boosting_model.fit(X_train, y_train)

y_pred = boosting_model.predict(X_test)

print("\nAdaBoost (Boosting) Classification Report:")
print(classification_report(y_test, y_pred))

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report


# Apply Gradient Boosting Classifier
boosting_model = GradientBoostingClassifier(random_state=42, n_estimators=100)
boosting_model.fit(X_train, y_train)

y_pred = boosting_model.predict(X_test)

print("\nGradient Boosting (Boosting) Classification Report:")
print(classification_report(y_test, y_pred))



#Cross Validation - Random Forest

from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Apply Cross Validation with Random Forest
cv_model = RandomForestClassifier(random_state=42)

# Perform 5-fold cross validation
cv_scores = cross_val_score(cv_model, X_train, y_train, cv=5, scoring='accuracy')

cv_model.fit(X_train, y_train)
y_pred = cv_model.predict(X_test)

print(f"{cv_scores}")
print(classification_report(y_test, y_pred))

          ''')
    
def amt_4():
    print(Fore.RED + '''
          
#Clustering

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load the dataset
anime_data = pd.read_csv("anime_data.csv")

# Explore the dataset
print(anime_data.describe())
print(anime_data.columns)

# Prepare data for clustering
numerical_cols = ['Score', 'Episodes', 'Duration_min',]

anime_data_copy = anime_data.copy()
anime_data_copy['Episodes'] = pd.to_numeric(anime_data_copy['Episodes'], errors='coerce')
anime_data_copy['Duration_min'] = anime_data_copy['Duration'].str.extract(r'(\d+)').astype(float)

new_data = anime_data_copy[numerical_cols].dropna()

print(new_data.head())




#K-Means


# K-Means clustering

kmeans = KMeans(n_clusters=4, random_state=42)
kmeans.fit(new_data)

# Add cluster labels to the cleaned data
new_data_with_clusters = new_data.copy()
new_data_with_clusters['kmeans_cluster'] = kmeans.labels_
print("Number of data points:", len(new_data_with_clusters))

# Elbow method to find optimal k
wss = []
for k in range(1, 16):
   kmeans = KMeans(n_clusters=k, random_state=42)
   kmeans.fit(new_data)
   wss.append(kmeans.inertia_)

plt.plot(range(1, 16), wss, marker='o')
plt.xlabel('Number of clusters k')
plt.ylabel('Total within-clusters sum of square')
plt.show()



# Standardize the data
scaler = StandardScaler()
X_std = scaler.fit_transform(new_data)

# Reduce dimensions for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_std)


# Visualize the clusters
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=kmeans.labels_, cmap='viridis')
plt.title('K-means Clustering')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.show()


#Agglomerative Clustering

agglomerative = AgglomerativeClustering(n_clusters=3)
hierarchical_labels = agglomerative.fit_predict(new_data)

# Add hierarchical cluster labels to the data
new_data_with_clusters['hierarchical_cluster'] = hierarchical_labels

# Visualize Hierarchical clusters using PCA-reduced data
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=hierarchical_labels, cmap='viridis', alpha=0.6, s=50)
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('Hierarchical Clustering')
plt.show()



silhoutte_avg = silhouette_score(new_data, hierarchical_labels)
print(f'Silhouette Score for Hierarchical Clustering: {silhoutte_avg}




#DBSCAN CLustering

from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=1.5, min_samples=5)
dbscan_labels = dbscan.fit_predict(new_data)

new_data_with_clusters['dbscan_cluster'] = dbscan_labels

plt.scatter(X_pca[:, 0], X_pca[:, 1], c=dbscan_labels, cmap='coolwarm', alpha=0.6, s=50)
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('DBSCAN Clustering')
plt.show()

silhouette_avg_dbscan = silhouette_score(new_data, dbscan_labels)
print("Mean Silhouette Width for DBSCAN Clustering:", silhouette_avg_dbscan)
          ''')
    
def amt_5():
    print(Fore.RED + '''
          
#CURE Clustering

import pandas as pd
from pyclustering.cluster.cure import cure
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

url = "https://raw.githubusercontent.com/uiuc-cse/data-fa14/gh-pages/data/iris.csv"
df = pd.read_csv(url)

df = df.drop(["species"], axis=1)
df = df.drop_duplicates()

print(df.head())

data = df.values.tolist()
cure_instance = cure(data, 3)
cure_instance.process()

clusters = cure_instance.get_clusters()
cluster_labels = np.full(len(data), fill_value=-1, dtype=int)
for cluster_id, cluster in enumerate(clusters):
    cluster_labels[cluster] = cluster_id

pca = PCA(n_components=2)
reduced_data = pca.fit_transform(df)

plt.figure(figsize=(7.5, 5))
scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=cluster_labels)
plt.xlabel('Petal length, Petal width')
plt.ylabel('Sepal length, Sepal width')
plt.title('Cure Clustering on Iris Dataset')
plt.show()



#Scatter Plot

import pandas as pd
from pyclustering.cluster.cure import cure
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv(url)

df = df.drop(["species"], axis=1)
df = df.drop_duplicates()

data = df.values.tolist()
cure_instance = cure(data, 3)
 cure_instance.process()

clusters = cure_instance.get_clusters()
cluster_labels = np.full(len(data), fill_value=-1, dtype=int)
for cluster_id, cluster in enumerate(clusters):
    cluster_labels[cluster] = cluster_id

pca = PCA(n_components=2)
reduced_data = pca.fit_transform(df)

plt.figure(figsize=(10, 7))
for cluster_id in np.unique(cluster_labels):
    plt.scatter(
        reduced_data[cluster_labels == cluster_id, 0],
        reduced_data[cluster_labels == cluster_id, 1],
        label=f'Cluster {cluster_id}'
    )
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('CURE Clustering on Iris Dataset')
plt.legend()
plt.show()

          ''')
    
def amt_6():
    print(Fore.RED + '''
          
#Recommendation Engine

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import ast  

df = pd.read_csv("games.csv")
df = df.drop_duplicates(subset='Title').reset_index(drop=True)

for col in ['Genres', 'Team', 'Summary']:
    df[col] = df[col].fillna('')

df['Genres'] = df['Genres'].apply(lambda x: ' '.join(ast.literal_eval(x)) if x.startswith('[') else x)
df['Team'] = df['Team'].apply(lambda x: ' '.join(ast.literal_eval(x)) if x.startswith('[') else x)
df['combined'] = df['Genres'] + ' ' + df['Team'] + ' ' + df['Summary']

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
indices = pd.Series(df.index, index=df['Title']).drop_duplicates()

def get_recommendations(title, cosine_sim=cosine_sim):
    idx = indices.get(title)
    if idx is None:
        return f"Game '{title}' not found in dataset."

    if isinstance(idx, pd.Series):
        idx = idx.iloc[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:10]

    game_indices = [i for i, _ in sim_scores]
    return df.iloc[game_indices][['Title', 'Genres', 'Team', 'Rating']]

print(get_recommendations("Need for Speed: Hot Pursuit"))


          ''')

def amt_7():
    print(Fore.RED + '''
          
#Collborative Filtering

import pandas as pd

df = pd.read_csv('fashion_products.csv')
df.columns = df.columns.str.strip()
df['Product'] = df['Product Name'].str.strip() + ' - ' + df['Brand'].str.strip()
df_cleaned = df[['User ID', 'Product', 'Rating']]

utility_matrix = df_cleaned.pivot_table(index='User ID', columns='Product', values='Rating').fillna(0)
print(utility_matrix)


from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

product_similarity = cosine_similarity(utility_matrix)
product_similarity_df = pd.DataFrame(product_similarity, index=utility_matrix.index, columns=utility_matrix.index)
print(product_similarity_df.head())

def recommend_products_for_user(user_id, utility_matrix, similarity_matrix, top_n=5):
    if user_id not in utility_matrix.index:
        print(f"User {user_id} not found.")
        return []
        
    similar_users = similarity_matrix.loc[user_id].drop(user_id)
    scores = pd.Series(0, index=utility_matrix.columns)

    for other_user, similarity in similar_users.items():
        scores += utility_matrix.loc[other_user] * similarity

    total_similarity = similar_users.sum()
    if total_similarity > 0:
        scores /= total_similarity

    rated = utility_matrix.loc[user_id]
    scores[rated > 0] = 0
    return scores.sort_values(ascending=False).head(top_n)

recommendations = recommend_products_for_user(1, utility_matrix, product_similarity_df, top_n=5)
print(recommendations)

          ''')  
    
def amt_8():
    print(Fore.RED + '''

#Apriori Association

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.impute import SimpleImputer

data = pd.read_csv("./groceries.csv")
print(data.head())
print(data.columns)
transactions = data.values.astype(str).tolist()
transactions = [[item for item in row if item != 'nan'] for row in transactions]
print(transactions[:10])

te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)
print(df.head(5))
print(df.shape)
frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
frequent_itemsets.count()['itemsets']

plt.figure(figsize=(12,6))
plt.xticks(rotation=90)
sns.barplot(x='itemsets', y='support', data=frequent_itemsets.nlargest(n = 15, columns = 'support'))
plt.show()

rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
rules.sort_values(by=['support'], ascending=False)
print("RULES 1:\n",rules)
rules["antecedent_len"] = rules["antecedents"].apply(lambda x: len(x))
rules["consequent_len"] = rules["consequents"].apply(lambda x: len(x))

print("RULES 2:\n",rules)
filtered_rules = rules[rules['antecedent_len'] >= 2]

print("RULES 3:\n", filtered_rules)
rules[ (rules['antecedent_len'] >= 2) &
       (rules['confidence'] > 0.3) &
       (rules['lift'] > 1) ].sort_values(by=['lift', 'support'], ascending=False)
print("RULES 4:\n",rules)
rules[ (rules['consequent_len'] >= 2) &
       (rules['lift'] > 1) ].sort_values(by=['lift', 'confidence'], ascending=False)
print("RULES 5:\n",rules)

rules['lift'] = rules['support'] / (rules['antecedent_len'] * rules['consequent_len'])
print(rules)

print("---------------------ACCURACY METRICS-------------------------------")
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
print(rules)
rules = association_rules(frequent_itemsets,metric="confidence",min_threshold=1)
print(rules)
rules = association_rules(frequent_itemsets,metric="leverage",min_threshold=1)
print(rules)
rules = association_rules(frequent_itemsets,metric="conviction",min_threshold=1)
print(rules)





#Apriori Example 2

import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# Load dataset
retail_df = pd.read_csv("genshin_transactions.csv")

# Group transactions
transactions = retail_df.groupby('Transaction_ID')['Item'].apply(list).tolist()

# Display sample transactions (optional)
grouped = retail_df.groupby('Transaction_ID')['Item'].apply(list).reset_index()
for _, row in grouped.head(5).iterrows():
    print(f"{row['Transaction_ID']} : {', '.join(row['Item'])}")

# One-hot encode transactions
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
encoded_df = pd.DataFrame(te_ary, columns=te.columns_)

print("\nOne-Hot Encoded DataFrame:")
print(encoded_df.head())

# Apriori to find frequent itemsets
min_support = 0.1
frequent_itemsets = apriori(encoded_df, min_support=min_support, use_colnames=True, max_len=3)
print("\nFrequent Itemsets:")
print(frequent_itemsets.head(10))

# Generate association rules by confidence
min_confidence = 0.7
rules_conf = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

print(f"\nAssociation Rules (min confidence={min_confidence}):")
if rules_conf.empty:
    print("No rules found with specified thresholds.")
else:
    for idx, row in rules_conf.reset_index(drop=True).iterrows():
        antecedents = list(row['antecedents'])
        consequents = list(row['consequents'])
        combined_items = antecedents + consequents
        # Counts: numerator = count(A and B), denominator = count(A)
        num_count = int(encoded_df[combined_items].all(axis=1).sum())
        den_count = int(encoded_df[antecedents].all(axis=1).sum())
        conf = (num_count / den_count) if den_count > 0 else 0.0

        ant_str = ", ".join(antecedents)
        cons_str = ", ".join(consequents)
        print(f"Rule {idx+1}: {ant_str} → {cons_str} = {num_count}/{den_count} = {conf:.2f}")

# Generate association rules by lift
min_lift = 1.5
rules_lift = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)

print(f"\nAssociation Rules (min lift={min_lift}):")
if rules_lift.empty:
    print("No rules found with specified lift threshold.")
else:
    for idx, row in rules_lift.reset_index(drop=True).iterrows():
        antecedents = list(row['antecedents'])
        consequents = list(row['consequents'])
        combined_items = antecedents + consequents
        num_count = int(encoded_df[combined_items].all(axis=1).sum())
        den_count = int(encoded_df[antecedents].all(axis=1).sum())
        conf = (num_count / den_count) if den_count > 0 else 0.0


        ant_str = ", ".join(antecedents)
        cons_str = ", ".join(consequents)
        lift = row['lift']
        print(f"Rule {idx+1}: {ant_str} → {cons_str} | support: {row['support']:.3f} | confidence: {conf:.2f} | lift: {lift:.2f}")
          
          ''')
    
def amt_9():
    print(Fore.RED + '''
          
#Page Rank Algorithm

def pagerank(graph, iterations, damping=0.85, tol=1e-6):
    N = len(graph)
    ranks = {node: 1.0 for node in graph}

    for iteration in range(iterations):
        print(f"Iteration {iteration + 1}:")
        for node, rank in ranks.items():
            print(f"  {node}: {rank:.6f}")
       
        new_ranks = {}
        for node in graph:
            sum_rank = 0.0
            for src in graph:
                if node in graph[src]:
                    sum_rank += ranks[src] / len(graph[src])
            new_ranks[node] = (1 - damping) / N + damping * sum_rank

        diff = sum(abs(new_ranks[node] - ranks[node]) for node in graph)
        ranks = new_ranks
    
        if diff < tol:
            print(f"Converged after {iteration + 1} iterations")
            break

    print("Final stable PageRank values:")
    for node, rank in ranks.items():
        print(f"  {node}: {rank:.6f}")
    return ranks

def input_graph():
    graph = {}
    n = int(input("Enter the number of pages: "))
    for _ in range(n):
        page = input("Enter page name: ")
        out_links = input("Enter outbound links from this page, separated by spaces: ").split()
        graph[page] = out_links
    return graph

graph = input_graph()
iterations = int(input("Enter number of iterations for PageRank calculation: "))

result = pagerank(graph, iterations)

          ''')
    
def amt_10():
    print(Fore.RED + '''
          
#Minhashing - R Implementation

library(textreuse)
minhash <- minhash_generator(n=240, seed=3552)
head(minhash(c("turn tokens into", "tokens into hashes", "into hashes fast")))

dir <- system.file("extdata/ats", package="textreuse")
corpus <- TextReuseCorpus(dir= dir, tokenizer=tokenize_ngrams, n =5, minhash_func = minhash, keep_tokens=TRUE, progress=FALSE)
head(minhashes(corpus[[1]]))

length(minhashes(corpus[[1]]))
lsh_threshold(h = 200, b = 50)
lsh_threshold(h = 240, b = 80)
lsh_probability(h = 240, b = 80, s = 0.25)
lsh_probability(h = 240, b = 80, s = 0.75)

buckets <- lsh(corpus, bands = 80, progress = FALSE)
buckets

baxter_matches <- lsh_query(buckets, "calltounconv00baxt")
baxter_matches

candidates <- lsh_candidates(buckets)
candidates




#Minhashing - Python Implementation

import os
import re
from datasketch import MinHash, MinHashLSH

folder = 'british-fiction-corpus'

def get_shingles(text, k=5):
    text = re.sub(r'\s+', ' ', text.lower())  
    return [text[i:i+k].encode('utf-8') for i in range(len(text) - k + 1)]

lsh = MinHashLSH(threshold=0.1, num_perm=100)
signatures = {}

for filename in os.listdir(folder):
    if filename.endswith('.txt'):
        with open(os.path.join(folder, filename), 'r', encoding='utf-8') as f:
            shingles = get_shingles(f.read())
        
            minhash = MinHash(num_perm=100)
            for shingle in shingles:
                minhash.update(shingle)           
            signatures[filename] = minhash
            lsh.insert(filename, minhash)

print(f"Loaded {len(signatures)} documents")

all_similarities = []
processed = set()

for doc_name in signatures:
    if doc_name in processed:
        continue

    similar_docs = lsh.query(signatures[doc_name])   
    for similar_doc in similar_docs:
        if similar_doc != doc_name and (doc_name, similar_doc) not in processed:
            sim = signatures[doc_name].jaccard(signatures[similar_doc])
            all_similarities.append((sim, doc_name, similar_doc))
            processed.add((doc_name, similar_doc))
            processed.add((similar_doc, doc_name))

top_5 = sorted(all_similarities, reverse=True)[:5]

print("\nTop 5 most similar document pairs:")
for sim, d1, d2 in top_5:
    print(f"{d1} <-> {d2}: similarity = {sim:.3f}")

          ''')