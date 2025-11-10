#!/usr/bin/env python
# coding: utf-8

# In[38]:


from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


# In[27]:


from sklearn import datasets
cancer = datasets.load_breast_cancer()


# In[28]:


print("Features: ", cancer.feature_names)
print("Labels: ", cancer.target_names)


# In[29]:


cancer.data.shape


# In[30]:


print(cancer.data[0:5])


# In[31]:


print(cancer.target)


# In[32]:


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(cancer.data, cancer.target, test_size=0.3,random_state=109) 


# In[33]:


from sklearn import svm
clf = svm.SVC(kernel='linear') 
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)


# In[34]:


from sklearn import metrics
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print("Precision:",metrics.precision_score(y_test, y_pred))
print("Recall:",metrics.recall_score(y_test, y_pred))
print("f1_score:",metrics.f1_score(y_test, y_pred, average="weighted"))


# In[35]:


from sklearn.metrics import confusion_matrix, classification_report

y_pred = clf.predict(X_test)

cm = confusion_matrix(y_test, y_pred)

print("Confusion Matrix:\n", cm)
print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=cancer.target_names))


# In[39]:


labels = ["Malignant", "benjign"]
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot(cmap="Blues")
disp.ax_.set_title("Confusion Matrix (SVM)")

