#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression



# In[2]:


df_sal = pd.read_csv('Salary_Data.csv')
df_sal.head()


# In[3]:


df_sal.describe()


# In[4]:


plt.title('Salary Distribution Plot')
sns.distplot(df_sal['Salary'])
plt.show()


# In[5]:


plt.scatter(df_sal['YearsExperience'], df_sal['Salary'], color = 'lightcoral')
plt.title('Salary vs Experience')
plt.xlabel('Years of Experienece')
plt.ylabel('Salary')
plt.box(False)
plt.show()


# In[6]:


X = df_sal.iloc[:, :1]  
y = df_sal.iloc[:, 1:] 


# In[7]:


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)


# In[8]:


regressor = LinearRegression()
regressor.fit(X_train , y_train)


# In[9]:


y_pred_test = regressor.predict(X_test)
y_pred_train = regressor.predict(X_train)


# In[10]:


plt.scatter(X_train,y_train,color = 'lightcoral')
plt.plot(X_train,y_pred_train,color = 'firebrick')
plt.title('Salary vs Experience (Training set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.legend(['X_train/pred(y_test)' , 'X_train/y_train'] , title = 'sal/Exp' , loc='best' ,facecolor ='white')
plt.box(False)
plt.show()


# In[11]:


plt.scatter(X_test, y_test, color = 'lightcoral')
plt.plot(X_train, y_pred_train, color = 'firebrick')
plt.title('Salary vs Experience (Test Set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.legend(['X_train/Pred(y_test)', 'X_train/y_train'], title = 'Sal/Exp', loc='best', facecolor='white')
plt.box(False)
plt.show()


# In[12]:


print(f'Coefficient: { regressor.coef_}')
print(f'Intercept: {regressor.intercept_}')

