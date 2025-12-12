from sklearn.datasets import load_iris
from sklearn import tree
iris = load_iris()
X, y = iris.data, iris.target
clf = tree.DecisionTreeClassifier(splitter='best', min_weight_fraction_leaf=1, min_impurity_decrease=2)
clf = clf.fit(X, y)

