#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np 
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import classification_report


# In[2]:


data = load_breast_cancer()
df = pd.DataFrame(data['data'],columns=data['feature_names'])
df['target'] = data['target']
df.head(5)


# In[6]:


kf = KFold(n_splits=5, shuffle=True, random_state=42)
X = df.drop('target',axis=1)
y = df['target']
for train_index,val_index in kf.split(X):
    X_train,X_val = X.iloc[train_index],X.iloc[val_index],
    y_train,y_val = y.iloc[train_index],y.iloc[val_index]


# In[7]:


ada_clf = AdaBoostClassifier()
ada_clf.get_params()



# In[8]:


ada_clf.fit(X_train,y_train)
predictions = ada_clf.predict(X_val)


# In[10]:


from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_val, predictions)

print("Confusion Matrix:")
print(cm)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Class 0', 'Class 1'],
            yticklabels=['Class 0', 'Class 1'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix Heatmap')
plt.show()


# In[9]:


print(classification_report(y_val,predictions))


# In[ ]:




