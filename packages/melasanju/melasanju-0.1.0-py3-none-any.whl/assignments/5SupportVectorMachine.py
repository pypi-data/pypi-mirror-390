{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 38,
   "id": "8df4a60c",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "407058cb",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn import datasets\n",
    "cancer = datasets.load_breast_cancer()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "a07b400d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Features:  ['mean radius' 'mean texture' 'mean perimeter' 'mean area'\n",
      " 'mean smoothness' 'mean compactness' 'mean concavity'\n",
      " 'mean concave points' 'mean symmetry' 'mean fractal dimension'\n",
      " 'radius error' 'texture error' 'perimeter error' 'area error'\n",
      " 'smoothness error' 'compactness error' 'concavity error'\n",
      " 'concave points error' 'symmetry error' 'fractal dimension error'\n",
      " 'worst radius' 'worst texture' 'worst perimeter' 'worst area'\n",
      " 'worst smoothness' 'worst compactness' 'worst concavity'\n",
      " 'worst concave points' 'worst symmetry' 'worst fractal dimension']\n",
      "Labels:  ['malignant' 'benign']\n"
     ]
    }
   ],
   "source": [
    "print(\"Features: \", cancer.feature_names)\n",
    "print(\"Labels: \", cancer.target_names)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "32adde0a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(569, 30)"
      ]
     },
     "execution_count": 29,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "cancer.data.shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "be1bd5c7",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[1.799e+01 1.038e+01 1.228e+02 1.001e+03 1.184e-01 2.776e-01 3.001e-01\n",
      "  1.471e-01 2.419e-01 7.871e-02 1.095e+00 9.053e-01 8.589e+00 1.534e+02\n",
      "  6.399e-03 4.904e-02 5.373e-02 1.587e-02 3.003e-02 6.193e-03 2.538e+01\n",
      "  1.733e+01 1.846e+02 2.019e+03 1.622e-01 6.656e-01 7.119e-01 2.654e-01\n",
      "  4.601e-01 1.189e-01]\n",
      " [2.057e+01 1.777e+01 1.329e+02 1.326e+03 8.474e-02 7.864e-02 8.690e-02\n",
      "  7.017e-02 1.812e-01 5.667e-02 5.435e-01 7.339e-01 3.398e+00 7.408e+01\n",
      "  5.225e-03 1.308e-02 1.860e-02 1.340e-02 1.389e-02 3.532e-03 2.499e+01\n",
      "  2.341e+01 1.588e+02 1.956e+03 1.238e-01 1.866e-01 2.416e-01 1.860e-01\n",
      "  2.750e-01 8.902e-02]\n",
      " [1.969e+01 2.125e+01 1.300e+02 1.203e+03 1.096e-01 1.599e-01 1.974e-01\n",
      "  1.279e-01 2.069e-01 5.999e-02 7.456e-01 7.869e-01 4.585e+00 9.403e+01\n",
      "  6.150e-03 4.006e-02 3.832e-02 2.058e-02 2.250e-02 4.571e-03 2.357e+01\n",
      "  2.553e+01 1.525e+02 1.709e+03 1.444e-01 4.245e-01 4.504e-01 2.430e-01\n",
      "  3.613e-01 8.758e-02]\n",
      " [1.142e+01 2.038e+01 7.758e+01 3.861e+02 1.425e-01 2.839e-01 2.414e-01\n",
      "  1.052e-01 2.597e-01 9.744e-02 4.956e-01 1.156e+00 3.445e+00 2.723e+01\n",
      "  9.110e-03 7.458e-02 5.661e-02 1.867e-02 5.963e-02 9.208e-03 1.491e+01\n",
      "  2.650e+01 9.887e+01 5.677e+02 2.098e-01 8.663e-01 6.869e-01 2.575e-01\n",
      "  6.638e-01 1.730e-01]\n",
      " [2.029e+01 1.434e+01 1.351e+02 1.297e+03 1.003e-01 1.328e-01 1.980e-01\n",
      "  1.043e-01 1.809e-01 5.883e-02 7.572e-01 7.813e-01 5.438e+00 9.444e+01\n",
      "  1.149e-02 2.461e-02 5.688e-02 1.885e-02 1.756e-02 5.115e-03 2.254e+01\n",
      "  1.667e+01 1.522e+02 1.575e+03 1.374e-01 2.050e-01 4.000e-01 1.625e-01\n",
      "  2.364e-01 7.678e-02]]\n"
     ]
    }
   ],
   "source": [
    "print(cancer.data[0:5])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "4475b7ec",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n",
      " 1 0 0 0 0 0 0 0 0 1 0 1 1 1 1 1 0 0 1 0 0 1 1 1 1 0 1 0 0 1 1 1 1 0 1 0 0\n",
      " 1 0 1 0 0 1 1 1 0 0 1 0 0 0 1 1 1 0 1 1 0 0 1 1 1 0 0 1 1 1 1 0 1 1 0 1 1\n",
      " 1 1 1 1 1 1 0 0 0 1 0 0 1 1 1 0 0 1 0 1 0 0 1 0 0 1 1 0 1 1 0 1 1 1 1 0 1\n",
      " 1 1 1 1 1 1 1 1 0 1 1 1 1 0 0 1 0 1 1 0 0 1 1 0 0 1 1 1 1 0 1 1 0 0 0 1 0\n",
      " 1 0 1 1 1 0 1 1 0 0 1 0 0 0 0 1 0 0 0 1 0 1 0 1 1 0 1 0 0 0 0 1 1 0 0 1 1\n",
      " 1 0 1 1 1 1 1 0 0 1 1 0 1 1 0 0 1 0 1 1 1 1 0 1 1 1 1 1 0 1 0 0 0 0 0 0 0\n",
      " 0 0 0 0 0 0 0 1 1 1 1 1 1 0 1 0 1 1 0 1 1 0 1 0 0 1 1 1 1 1 1 1 1 1 1 1 1\n",
      " 1 0 1 1 0 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 1 0 1 0 1 1 1 1 0 0 0 1 1\n",
      " 1 1 0 1 0 1 0 1 1 1 0 1 1 1 1 1 1 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 0\n",
      " 0 1 0 0 1 1 1 1 1 0 1 1 1 1 1 0 1 1 1 0 1 1 0 0 1 1 1 1 1 1 0 1 1 1 1 1 1\n",
      " 1 0 1 1 1 1 1 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 0 1 0 0 1 0 1 1 1 1 1 0 1 1\n",
      " 0 1 0 1 1 0 1 0 1 1 1 1 1 1 1 1 0 0 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1 0 1\n",
      " 1 1 1 1 1 1 0 1 0 1 1 0 1 1 1 1 1 0 0 1 0 1 0 1 1 1 1 1 0 1 1 0 1 0 1 0 0\n",
      " 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1 0 1 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1\n",
      " 1 1 1 1 1 1 1 0 0 0 0 0 0 1]\n"
     ]
    }
   ],
   "source": [
    "print(cancer.target)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "id": "edb424ff",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.model_selection import train_test_split\n",
    "X_train, X_test, y_train, y_test = train_test_split(cancer.data, cancer.target, test_size=0.3,random_state=109) "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "id": "a679d81f",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn import svm\n",
    "clf = svm.SVC(kernel='linear') \n",
    "clf.fit(X_train, y_train)\n",
    "y_pred = clf.predict(X_test)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "18505de0",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Accuracy: 0.9649122807017544\n",
      "Precision: 0.9811320754716981\n",
      "Recall: 0.9629629629629629\n",
      "f1_score: 0.9650224422036399\n"
     ]
    }
   ],
   "source": [
    "from sklearn import metrics\n",
    "print(\"Accuracy:\",metrics.accuracy_score(y_test, y_pred))\n",
    "print(\"Precision:\",metrics.precision_score(y_test, y_pred))\n",
    "print(\"Recall:\",metrics.recall_score(y_test, y_pred))\n",
    "print(\"f1_score:\",metrics.f1_score(y_test, y_pred, average=\"weighted\"))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "da9d8954",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Confusion Matrix:\n",
      " [[ 61   2]\n",
      " [  4 104]]\n",
      "\n",
      "Classification Report:\n",
      "               precision    recall  f1-score   support\n",
      "\n",
      "   malignant       0.94      0.97      0.95        63\n",
      "      benign       0.98      0.96      0.97       108\n",
      "\n",
      "    accuracy                           0.96       171\n",
      "   macro avg       0.96      0.97      0.96       171\n",
      "weighted avg       0.97      0.96      0.97       171\n",
      "\n"
     ]
    }
   ],
   "source": [
    "from sklearn.metrics import confusion_matrix, classification_report\n",
    "\n",
    "y_pred = clf.predict(X_test)\n",
    "\n",
    "cm = confusion_matrix(y_test, y_pred)\n",
    "\n",
    "print(\"Confusion Matrix:\\n\", cm)\n",
    "print(\"\\nClassification Report:\\n\", classification_report(y_test, y_pred, target_names=cancer.target_names))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "id": "83e30528",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "Text(0.5, 1.0, 'Confusion Matrix (SVM)')"
      ]
     },
     "execution_count": 39,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAAjcAAAHFCAYAAAAOmtghAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjAsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvlHJYcgAAAAlwSFlzAAAPYQAAD2EBqD+naQAASqxJREFUeJzt3X18z/X+x/Hnd7Nr2zDZhYaRy1wtVyFNx0UJR3VOEZWhIhclVx1HZdUxESN0iDI7Csc5UXJK5CqJXEdIuV5lTWIbw2x7//7Qvj/fNmz7fmf22ePe7XO7+bw/78/n8/p+G15e7/f787EZY4wAAAAswq24AwAAAHAlkhsAAGApJDcAAMBSSG4AAIClkNwAAABLIbkBAACWQnIDAAAsheQGAABYCskNAACwFJIbIA+7d+9Wnz59FBERIW9vb5UtW1Z33HGHJk6cqN9++61I771z505FRUUpMDBQNptNU6dOdfk9bDabYmJiXH7d65k3b55sNptsNpvWrVuX67gxRrfddptsNpvatm1bqHv885//1Lx58wp0zrp1664akzNeffVV1atXT9nZ2fa2U6dOafTo0apXr578/PwUGBioOnXq6PHHH9fu3bslSQ8++KB8fHx05syZq167V69e8vDw0C+//CJJ9u81Ojr6qrHk9Dl69Ki9/fHHH9cDDzzg7EcFbi4GgIPZs2ebMmXKmNtvv9289dZbZu3atWblypUmNjbWREREmAceeKBI79+4cWNTs2ZN88knn5hNmzaZEydOuPwemzZtMomJiS6/7vXEx8cbScbf39889thjuY6vXbvWfjwqKqpQ97j99tsLfG5KSorZtGmTSUlJKdQ98/LTTz8ZPz8/85///MfelpaWZm677TYTEhJiJk+ebD7//HPz8ccfm8mTJ5vWrVubhIQEY4wxH3/8sZFk3nrrrTyvfebMGePj4+Pws5jzvfn6+prU1FSH/tnZ2SYiIsIEBAQYSebIkSP2YwcPHjRlypQxq1evdtlnB4obyQ1wha+++sq4u7ub++67z1y4cCHX8YsXL5qPPvqoSGMoU6aMeeaZZ4r0HsUlJ7l58sknjY+PT65k4rHHHjMtW7YsVIKSoyDnZmRkmEuXLhXqPtczatQoU7lyZZOVlWVvmzt3rpFk1qxZk+c5OX0zMzNNWFiYadKkSZ79Zs6caSSZjz/+2N4myTz22GPGx8fHzJ4926H/559/biSZp556KldyY4wxXbp0MR06dCjMxwRuSgxLAVeIjY2VzWbT7Nmz5eXlleu4p6en/vznP9v3s7OzNXHiRNWpU0deXl6qVKmSnnjiCf34448O57Vt21b169fX1q1b1aZNG/n6+qp69ep6/fXX7UMWOUM2mZmZmjlzpn0IQZJiYmLsv75SzjlXDjOsWbNGbdu2VVBQkHx8fFSlShX95S9/UXp6ur1PXsNS3377rbp166by5cvL29tbjRs3VkJCgkOfnOGbhQsXasyYMQoLC1NAQIDat2+vAwcO5O9LlvToo49KkhYuXGhvS0lJ0QcffKC+ffvmec4rr7yiFi1aqEKFCgoICNAdd9yhd999V+aKd/9Wq1ZNe/fu1fr16+3fX7Vq1Rxinz9/voYPH67KlSvLy8tLBw8ezDUs9euvvyo8PFytWrXSpUuX7Nfft2+f/Pz89Pjjj1/z82VkZOjdd99Vz5495eb2/3/Mnjp1SpIUGhqa53k5fd3d3dW7d29t375de/bsydUvPj5eoaGh6tSpk0N7YGCgHnzwQc2dO9ehfe7cuWrdurVq1aqV530ff/xxff755zp06NA1PxdQUpDcAL/LysrSmjVr1KRJE4WHh+frnGeeeUYvvPCCOnTooGXLlum1117TihUr1KpVK/36668OfZOSktSrVy899thjWrZsmTp16qTRo0frvffekyR17txZmzZtkiT99a9/1aZNm+z7+XX06FF17txZnp6emjt3rlasWKHXX39dfn5+ysjIuOp5Bw4cUKtWrbR3715NmzZNS5YsUb169RQdHa2JEyfm6v/3v/9dx44d0zvvvKPZs2frhx9+UNeuXZWVlZWvOAMCAvTXv/7V4S/hhQsXys3NTd27d7/qZ+vfv78WL16sJUuW6KGHHtKQIUP02muv2fssXbpU1atXV2RkpP37W7p0qcN1Ro8erePHj2vWrFn6+OOPValSpVz3qlixohYtWqStW7fqhRdekCSlp6fr4YcfVpUqVTRr1qxrfr6vv/5ap06d0j333OPQ3rJlS0nSE088oQ8//NCe7OSlb9++stlsuRKVffv2acuWLerdu7fc3d1zndevXz9t3rxZ+/fvlySdOXNGS5YsUb9+/a56r7Zt28oYo08++eSanwsoMYq7dATcLJKSkowk06NHj3z1379/v5Fk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ad26dbLZbDpz5kyxxgVcT9u2bTV06NAivUdMTIwaN25s34+OjtYDDzxQpPcEihLJDW5a0dHRstlsGjBgQK5jAwcOlM1mU3R0dKGu3apVK504ceKGPEyroObNm6dy5coVdxgoRUaMGKHVq1fb9998803Nmzev+AICnERyg5taeHi4Fi1apPPnz9vbLly4oIULF6pKlSqFvm7Ou1d4jQUglS1bVkFBQfb9wMBAEmyUaCQ3uKndcccdqlKlipYsWWJvW7JkicLDwxUZGWlvW7Fihe666y6VK1dOQUFB6tKliw4dOnTV6+Y1LDVnzhyFh4fL19dXDz74oOLi4hz+gM8p3c+fP1/VqlVTYGCgevToYX+haX7iyBkeW7Jkie655x75+vqqUaNG2rRpkz2uPn36KCUlRTabTTabTTExMU58g7CCzMxMDR482P5z9eKLL9rfKp2RkaFRo0apcuXK8vPzU4sWLbRu3Tr7uTmVwM8++0x169ZV2bJldd999+nEiRP2PtcblkpLS1OvXr3k5+en0NBQTZkyJddwWbVq1RQbG6u+ffvK399fVapU0ezZs4vqKwGuieQGN70+ffooPj7evj937lz17dvXoc+5c+c0bNgwbd26VatXr5abm5sefPBBZWdn5+seGzdu1IABA/Tcc89p165d6tChg8aNG5er36FDh/Thhx9q+fLlWr58udavX6/XX3+9wHGMGTNGI0aM0K5du1SrVi09+uijyszMVKtWrTR16lQFBAToxIkTOnHihEaMGFGQrwsWlJCQoDJlyujrr7/WtGnTNGXKFL3zzjuSLv/+2LhxoxYtWqTdu3fr4Ycf1n333acffvjBfn56eromTZqk+fPn64svvtDx48cL9HM1bNgwbdy4UcuWLdOqVau0YcMG7dixI1e/yZMnq2nTptq5c6cGDhyoZ555Rt99953zXwBQUAa4SfXu3dt069bNnDx50nh5eZkjR46Yo0ePGm9vb3Py5EnTrVs307t37zzPTU5ONpLMnj17jDHGHDlyxEgyO3fuNMYYs3btWiPJnD592hhjTPfu3U3nzp0drtGrVy8TGBho3x87dqzx9fU1qamp9raRI0eaFi1aXPUzXC2Od955x95n7969RpLZv3+/McaY+Ph4h/uidIuKijJ169Y12dnZ9rYXXnjB1K1b1xw8eNDYbDbz008/OZzTrl07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9ttvG2OMadmypRkwYIDD8RYtWphGjRrlee/U1FTj5eVl5syZk2ecR44cMZLMzp07HdrDw8PNggULHNpee+0107JlS2OMMW+//bapUKGCOXfunP34zJkz87zWlapWrWqmTJly1eOLFy82QUFB9v34+HgjyWzevNnetn//fiPJfP3118YYY9q0aWNiY2MdrjN//nwTGhpq35dkli5detX7AihazLkBLGL58uUqW7asMjMzdenSJXXr1k3Tp0+3H69atapuueUW+/727dt19uxZBQUFOVzn/PnzOnTokCRp//79GjBggMPxli1bau3atXnGsH//fl28eFHt2rXLd9wnT55UYmKi+vXrp6eeesrenpmZaZ/Ps3//fjVq1Ei+vr4OcRTU2rVrFRsbq3379ik1NVWZmZm6cOGCzp07Jz8/P0lSmTJl1LRpU/s5derUUbly5bR//341b95c27dv19atWx0qNVlZWbpw4YLS09MdYgRQPEhuAIu45557NHPmTHl4eCgsLCzXhOGcv7xzZGdnKzQ0VOvWrct1rcIuh/bx8SnwOdnZ2ZIuD021aNHC4Zi7u7uky2+vdtaxY8d0//33a8CAAXrttddUoUIFffnll+rXr5/D8J10eSn3H+W0ZWdn65VXXtFDDz2Uq4+3t7fTcQJwHskNYBF+fn667bbb8t3/jjvuUFJSksqUKaNq1arl2adu3bravHmznnjiCXvb5s2br3rNmjVrysfHR6tXr87zjeqenp6SLlc6cgQHB6ty5co6fPiwevXqled169Wrp/nz5+v8+fP2BOpaceRl27ZtyszM1OTJk+Xmdnm64eLFi3P1y8zM1LZt29S8eXNJ0oEDB3TmzBnVqVNH0uXv7cCBAwX6rgHcWCQ3QCnVvn17tWzZUg888IAmTJig2rVr6+eff9Ynn3yiBx54QE2bNtVzzz2n3r17q2nTprrrrrv0/vvva+/evapevXqe1/T29tYLL7ygUaNGydPTU61bt9bJkye1d+9e9evXT5UqVZKPj49WrFihW2+9Vd7e3goMDFRMTIyeffZZBQQEqFOnTrp48aK2bdum06dPa9iwYerZs6fGjBmjfv366cUXX9TRo0c1adKkAn3eGjVqKDMzU9OnT1fXrl21ceNGzZo1K1c/Dw8PDRkyRNOmTZOHh4cGDx6sO++8057svPzyy+rSpYvCw8P18MMPy83NTbt379aePXv0j3/8o+D/IwC4HKulgFLKZrPpk08+0d13362+ffuqVq1a6tGjh44ePWpf3dS9e3e9/PLLeuGFF9SkSRMdO3ZMzzzzzDWv+9JLL2n48OF6+eWXVbduXXXv3l3JycmSLs9nmTZtmt5++22FhYWpW7dukqQnn3xS77zzjubNm6cGDRooKipK8+bNsy8dL1u2rD7++GPt27dPkZGRGjNmjCZMmFCgz9u4cWPFxcVpwoQJql+/vt5//32NHz8+Vz9fX1+98MIL6tmzp1q2bCkfHx8tWrTIfvzee+/V8uXLtWrVKjVr1kx33nmn4uLiVLVq1QLFA6Do2IwrBrMBAABuElRuAACApZDcAAAASyG5AQAAlkJyAwAALIXkBgAAWArJDQAAsBSSGwAAYCkkNwAAwFJIbgAAgKWQ3AAAAEshuQEAAJZCcgMAACzl/wDcpHok8wZY+wAAAABJRU5ErkJggg==",
      "text/plain": [
       "<Figure size 640x480 with 2 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "labels = [\"Malignant\", \"benjign\"]\n",
    "cm = confusion_matrix(y_test, y_pred)\n",
    "disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)\n",
    "disp.plot(cmap=\"Blues\")\n",
    "disp.ax_.set_title(\"Confusion Matrix (SVM)\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "base",
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
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
