{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "40a5c135",
   "metadata": {},
   "outputs": [
    {
     "ename": "NameError",
     "evalue": "name 'pd' is not defined",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mNameError\u001b[0m                                 Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[2], line 1\u001b[0m\n\u001b[1;32m----> 1\u001b[0m bank_data \u001b[38;5;241m=\u001b[39m \u001b[43mpd\u001b[49m\u001b[38;5;241m.\u001b[39mread_csv(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mbank-marketing.csv\u001b[39m\u001b[38;5;124m'\u001b[39m, sep\u001b[38;5;241m=\u001b[39m\u001b[38;5;124m'\u001b[39m\u001b[38;5;124m;\u001b[39m\u001b[38;5;124m'\u001b[39m)\n\u001b[0;32m      3\u001b[0m \u001b[38;5;66;03m# Map binary columns\u001b[39;00m\n\u001b[0;32m      4\u001b[0m bank_data[\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mdefault\u001b[39m\u001b[38;5;124m'\u001b[39m] \u001b[38;5;241m=\u001b[39m bank_data[\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mdefault\u001b[39m\u001b[38;5;124m'\u001b[39m]\u001b[38;5;241m.\u001b[39mmap({\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mno\u001b[39m\u001b[38;5;124m'\u001b[39m: \u001b[38;5;241m0\u001b[39m, \u001b[38;5;124m'\u001b[39m\u001b[38;5;124myes\u001b[39m\u001b[38;5;124m'\u001b[39m: \u001b[38;5;241m1\u001b[39m, \u001b[38;5;124m'\u001b[39m\u001b[38;5;124munknown\u001b[39m\u001b[38;5;124m'\u001b[39m: \u001b[38;5;241m0\u001b[39m})\n",
      "\u001b[1;31mNameError\u001b[0m: name 'pd' is not defined"
     ]
    }
   ],
   "source": [
    "bank_data = pd.read_csv('bank-marketing.csv', sep=';')\n",
    "\n",
    "# Map binary columns\n",
    "bank_data['default'] = bank_data['default'].map({'no': 0, 'yes': 1, 'unknown': 0})\n",
    "bank_data['y'] = bank_data['y'].map({'no': 0, 'yes': 1})\n",
    "\n",
    "# Encode categorical features\n",
    "bank_data = pd.get_dummies(bank_data, drop_first=True)\n",
    "\n",
    "\n",
    "x = bank_data.drop(columns=['y'])\n",
    "y = bank_data['y']\n",
    "x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)\n",
    "\n",
    "\n",
    "rf = RandomForestClassifier()\n",
    "rf.fit(x_train, y_train)\n",
    "y_pred = rf.predict(x_test)\n",
    "\n",
    "print(\"Accuracy:\", accuracy_score(y_test, y_pred))\n",
    "print(\"Precision:\", precision_score(y_test, y_pred))\n",
    "print(\"Recall:\", recall_score(y_test, y_pred))\n",
    "print(\"F1 Score:\", f1_score(y_test, y_pred))\n",
    "\n",
    "# Confusion Matrix\n",
    "cm = confusion_matrix(y_test, y_pred)\n",
    "disp = ConfusionMatrixDisplay(confusion_matrix=cm)\n",
    "disp.plot()\n",
    "\n",
    "# Export the first three decision trees from the forest\n",
    "\n",
    "for i in range(3):\n",
    "    tree = rf.estimators_[i]\n",
    "    dot_data = export_graphviz(tree,\n",
    "                               feature_names=x_train.columns,  \n",
    "                               filled=True,  \n",
    "                               max_depth=2, \n",
    "                               impurity=False, \n",
    "                               proportion=True)\n",
    "    graph = graphviz.Source(dot_data)\n",
    "    display(graph)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "81874067",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
