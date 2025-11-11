{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "3238badc",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[51 92 14 71 60 20 82 86 74 74]\n"
     ]
    }
   ],
   "source": [
    "#Fancy Indexing\n",
    "import numpy as np\n",
    "rand = np.random.RandomState(42)\n",
    "x = rand.randint(100, size=10)\n",
    "print(x)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "f4bbd887",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[71, 86, 14]"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "[x[3], x[7], x[2]]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "6727c3ab",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([71, 86, 60])"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ind = [3, 7, 4]\n",
    "x[ind]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "bfe33ec6",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[71, 86],\n",
       "       [60, 20]])"
      ]
     },
     "execution_count": 5,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ind = np.array([[3, 7],\n",
    "               [4, 5]])\n",
    "x[ind]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "15fb5169",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 0,  1,  2,  3],\n",
       "       [ 4,  5,  6,  7],\n",
       "       [ 8,  9, 10, 11]])"
      ]
     },
     "execution_count": 6,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "X = np.arange(12).reshape((3, 4))\n",
    "X"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "87d13b73",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 2,  5, 11])"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "row = np.array([0, 1, 2])\n",
    "col = np.array([2, 1, 3])\n",
    "X[row, col]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "a94075cc",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 2,  1,  3],\n",
       "       [ 6,  5,  7],\n",
       "       [10,  9, 11]])"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "X[row[:, np.newaxis], col]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "a825ca18",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[ 0  1  2  3]\n",
      " [ 4  5  6  7]\n",
      " [ 8  9 10 11]]\n"
     ]
    }
   ],
   "source": [
    "#Combined Indexing\n",
    "print(X)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "f2343c6f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([10,  8,  9])"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "X[2, [2, 0, 1]]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "5c877e57",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 6,  4,  5],\n",
       "       [10,  8,  9]])"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "X[1:, [2, 0, 1]]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "1f0c7c29",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 0,  2],\n",
       "       [ 4,  6],\n",
       "       [ 8, 10]])"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mask = np.array([1, 0, 1, 0], dtype=bool)\n",
    "X[row[:, np.newaxis], mask]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "73c28c1b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(100, 2)"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Example: Selecting Random Points\n",
    "mean = [0, 0]\n",
    "cov = [[1, 2],\n",
    "       [2, 5]]\n",
    "X = rand.multivariate_normal(mean, cov, 100)\n",
    "X.shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "0a1c978b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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WD0nJ8etZgFdbNiwQbfccovGjh2rhx9+2O3mOC4tgkhWVpaGDx8e8etffPGFtm7dqgsvvLDts5ycHA0ePFjV1dU90cSkE6tPwxYvXqzly5drzpw5uuOOO5jqisBqfyJ+4ZHN6upqDRkypO3z6upqRungGc8//7zuv/9+zZw5U4sXL+4ygpeKWKwq6bPPPtONN96ovXv3tn1WX1+vXbt28XJIwKJFi7R8+XItXLhQd955JyEEriovL1efPn20cePGts/q6+u1bds2TZw40cWWASesXLlS9957ry6//HI98sgjaRFCpDQZEYnl3HPPVVlZmRYuXKi77rpLoVBIixYtUkFBgb7//e+73byktHHjRj399NOaM2eOLrnkEh04cKDtayeddJJyc3NdbB3SUa9evXTFFVdo8eLFKiws1KBBg7Ro0SINGDBAM2fOdLt5SHO7du3SL37xC82cOVPXXnutDh482Pa13r17Ky8vz8XWOYsgohP/gXr66af14IMPat68eTp27JimTp2qBx54QH369HG7eUkpvO99xYoVWrFiRYevXX/99brhhhvcaBbS3I033qiWlhbdeeedampq0qRJk/TMM8+kzW+e8K5169bp+PHjWr9+fZe6NrNmzdIDDzzgUsuc5wtROhQAALiENSIAAMA1BBEAAOAagggAAHANQQQAALiGIAIAAFxDEAEAAK4hiAAAANcQRAAAgGsIIgAAwDUEEQAA4BqCCAAAcM3/By7JEwZLdABBAAAAAElFTkSuQmCC\n",
      "text/plain": [
       "<Figure size 640x480 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "%matplotlib inline\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn; seaborn.set() # for plot styling\n",
    "plt.scatter(X[:, 0], X[:, 1]);"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "0feea806",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([79, 55, 63, 69, 70, 88, 33, 26, 54, 64, 66, 75, 35, 87, 20,  9, 22,\n",
       "       92, 45, 78])"
      ]
     },
     "execution_count": 17,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "indices = np.random.choice(X.shape[0], 20, replace=False)\n",
    "indices"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "7e82b90d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(20, 2)"
      ]
     },
     "execution_count": 18,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "selection = X[indices] # fancy indexing here\n",
    "selection.shape\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "d3afa410",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAAiIAAAGgCAYAAACXJAxkAAAAOXRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjUuMiwgaHR0cHM6Ly9tYXRwbG90bGliLm9yZy8qNh9FAAAACXBIWXMAAA9hAAAPYQGoP6dpAABMmklEQVR4nO3deZDkdX0//ufn/vTdPTO7vbM3OyDLuYrrkYhi2CKpYGnKmKqE6AYVFQ+OSAAVUKggRoWAJyk51IgFEo9CgxBF/VVZUhV01fBFkWthd5llrp2enj4/9+f3R28Pc89096fn0z39fPyDdm9/Pu99z+x8nvM+Xm/B930fRERERCEQw24AERER9S4GESIiIgoNgwgRERGFhkGEiIiIQsMgQkRERKFhECEiIqLQMIgQERFRaBhEiIiIKDRy2A1YDd/34Xntq7smikJbr99r2J/BY58Gi/0ZPPZpsNZDf4qiAEEQVvxzXRFEPM9HLlduy7VlWUQmE0OhUIHjeG25Ry9hfwaPfRos9mfw2KfBWi/92dcXgyStHEQ4NUNEREShYRAhIiKi0DCIEBERUWgYRIiIiCg0DCJEREQUGgYRIiIiCg2DCBEREYWGQYSIiIhCwyBCREREoWEQISIiotC0LYg88MADOP/883HGGWfgLW95Cx5++OF23YqIiGhd8n0fpaqNqaKJUtWG7wd3/kw7r92Itpw188Mf/hDXXHMNPvaxj+HNb34zHnzwQVxxxRXYtGkTXvWqV7XjlkREROtKvmji4NFpTBYMOK4PWRLQn9SxY1MC6bjW2rVLJg6PFtty7UYFHkR838cXv/hFXHjhhbjwwgsBAB/5yEfwu9/9Dr/+9a8ZRIiIiFaQKxh4/OAxFCs20jEVqizBclyM5CooVCycsau/6cCQL5l44vlJlA0n8Gs3I/Ag8vzzz+Po0aN461vfOuf1u+++u6XrynJ7ZpEkSZzzX2oN+zN47NNgsT+Dxz4NligKeGY4j6rlYnN/FIJQO8FWUUREdRljU1UMT5TQn9Jn3lst3/cxPFGC0YZrNyvwIHLo0CEAQKVSwUUXXYQnn3wSW7duxYc+9CGce+65TV1TFAVkMrEAW7lQMhlp6/V7DfszeOzTYLE/g8c+DUahbGF8qorNGxKIaAsf07KqoFS1IWsqkjG14WtXbB9bssnAr92swINIqVQCAHzsYx/DJZdcgiuvvBI/+clP8OEPfxjf+MY38Gd/9mcNX9PzfBQKlaCbCqCW4JPJCAqFKlzXa8s9egn7M3js02CxP4PHPg3WdNmC7bhwbQEl21nwvuf5KBSrmDhWhGvpDV07VzBQKFahiYAb8LXnSyYjqxolCzyIKIoCALjooovw9re/HQBwyimn4Mknn2w6iACA47T3m9t1vbbfo5ewP4PHPg0W+zN47NNgiAKgyBIMy4EiSQveNywHoiBAFISG+7v+uarpQFcXRoBWrt2swCf0Nm3aBAB4xSteMef1E088EcPDw0HfjoiIaF2JRxRszESQL1kLttT6vo982UJ/UkdMb3wsIabL6E/qyJeDv3azAg8ip556KmKxGB5//PE5rz/zzDPYvn170LcjIiJaVwRBwNDWdG3xaL4Kw3LgeT4My8FYvoqYLmPHpkRTi0kFQcCOTQnE2nDtZgUeeXRdx/ve9z589atfRTabxZlnnokf//jHePTRR/HNb34z6NsRERGtO31JHXuGBmbqiBQqNmRJwGBftOVaH+m4hjN29c/UEQny2s1oy9jLhz/8YUQiEdx2220YGxvD0NAQvvzlL+N1r3tdO25HRES07qQTGs4c6kfZcGA7HhRZREyXAxmtSMc1pIbUtly7UW2bBHrPe96D97znPe26PBER0bonCALiEaXrrt0IVp8hIiKi0DCIEBERUWgYRIiIiCg0DCJEREQUGgYRIiIiCg2DCBEREYWGQYSIiIhCwyBCREREoWEQISIiotAwiBAREVFoGESIiIgoNAwiREREFBoGESIiIgoNgwgRERGFhkGEiIiIQsMgQkRERKFhECEiIqLQMIgQERFRaBhEiIiIKDQMIkRERBQaBhEiIiIKDYMIERERhYZBhIiIiELDIEJEREShYRAhIiKi0DCIEBERUWgYRIiIiCg0DCJEREQUGgYRIiIiCg2DCBEREYWGQYSIiIhCwyBCREREoWEQISIiotAwiBAREVFoGESIiIgoNAwiREREFBoGESIiIgpNW4PICy+8gFe96lX4wQ9+0M7bEBERUZdqWxCxbRtXXnklKpVKu25BREREXa5tQeTLX/4yYrFYuy5PRERE60BbgshvfvMb3H///fjc5z7XjssTERHROiEHfcFCoYCrr74a1113HQYHBwO7riy3Z/BGksQ5/6XWsD+Dxz4NFvszeOzTYPVa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8IaQWtXdLrjggrCb0NXqa74GBwfnvL5x40aMjIyE0aSud+655+Lcc88NuxnrQjKZXPAz8+GHH8aRI0dw9tlnh9SqtdETQWR4eBj79u1b8v1f/epX2LBhAwDgqquuwuWXX47/+I//wLvf/W488MADC35wUWN9CgA//elPcdttt2H//v3YvXv3WjSxqzTan9S4arUKAFBVdc7rmqat+984qfv89re/xTXXXIN9+/at+7DXE0Ekm83ioYceWvL9+pQMAJxyyikAgNtuuw1vfvOb8f3vfx+XXHJJ29vYbRrp0/vuuw833ngjzj//fHziE59Yi+Z1nUb6k5qj6zqA2lqR+v8GaovVI5FIWM0iWuBnP/sZrrzySuzZswe33npr2M1pu54IIoqiYGhoaMn3jx49ij/84Q/4q7/6q5nXIpEItm7divHx8bVoYtdZqU/rbrnlFtx5553Yv38/rr32Wk51LWG1/UnNq49sjo+PY/v27TOvj4+Pc5SOOsa3v/1t3HTTTTjvvPNwyy23LBjBW4+4WBXAn/70J1x22WU4cuTIzGuFQgEvvPACHw4tuPnmm3HnnXfi6quvxnXXXccQQqHavXs34vE4HnvssZnXCoUCnnzySezduzfElhHV3Hvvvbjxxhvxzne+E1/4whd6IoQAPTIispI3velNOPnkk3H11Vfjk5/8JHzfx80334xMJoN3vOMdYTevKz322GO46667sH//frztbW/DxMTEzHvRaBSxWCzE1lEvUlUV73rXu3DLLbegr68PW7Zswc0334xNmzbhvPPOC7t51ONeeOEFfOYzn8F5552Hiy++GJOTkzPv6bqORCIRYuvai0EEtR9Qd911Fz73uc/hoosugmVZOPvss/HZz34W8Xg87OZ1pfq+93vuuQf33HPPnPcuueQSXHrppWE0i3rcZZddBsdxcN1118EwDLzmNa/B3Xff3TO/eVLn+slPfgLbtvHII48sqGvz9re/HZ/97GdDaln7CT5LhxIREVFIuEaEiIiIQsMgQkRERKFhECEiIqLQMIgQERFRaBhEiIiIKDQMIkRERBQaBhEiIiIKDYMIERERhYZBhIiIiELDIEJEREShYRAhIiKi0Pz/89BELJiSFTIAAAAASUVORK5CYII=\n",
      "text/plain": [
       "<Figure size 640x480 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "plt.scatter(X[:, 0], X[:, 1], alpha=0.3)\n",
    "plt.scatter(selection[:, 0], selection[:, 1],\n",
    "            facecolor='none', s=200);"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "bf41687c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[ 0 99 99  3 99  5  6  7 99  9]\n"
     ]
    }
   ],
   "source": [
    "#Modifying Values with Fancy Indexing\n",
    "x = np.arange(10)\n",
    "i = np.array([2, 1, 8, 4])\n",
    "x[i] = 99\n",
    "print(x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "d60c0e03",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[ 0 89 89  3 89  5  6  7 89  9]\n"
     ]
    }
   ],
   "source": [
    "x[i] -= 10\n",
    "print(x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "541ecc51",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[6. 0. 0. 0. 0. 0. 0. 0. 0. 0.]\n"
     ]
    }
   ],
   "source": [
    "x = np.zeros(10)\n",
    "x[[0, 0]] = [4, 6]\n",
    "print(x)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "eba2201b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([6., 0., 1., 1., 1., 0., 0., 0., 0., 0.])"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "i = [2, 3, 3, 4, 4, 4]\n",
    "x[i] += 1\n",
    "x"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "fec059ba",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[0. 0. 1. 2. 3. 0. 0. 0. 0. 0.]\n"
     ]
    }
   ],
   "source": [
    "x = np.zeros(10)\n",
    "np.add.at(x, i, 1)\n",
    "print(x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "id": "83fc0382",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "#Example:Binning Data\n",
    "np.random.seed(42)\n",
    "x = np.random.random(100)\n",
    "# compute a histogram by hand\n",
    "bins = np.linspace(-5, 5, 20)\n",
    "counts = np.zeros_like(bins)\n",
    "# find the appropriate bin for each x\n",
    "i = np.searchsorted(bins, x)\n",
    "# add 1 to each of these bins\n",
    "np.add.at(counts, i, 1)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "id": "20d3379f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 640x480 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "\n",
    "# plot the results\n",
    "plt.plot(bins, counts);\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "id": "c72d3b56",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "NumPy routine:\n",
      "70.2 ms ± 922 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)\n",
      "Custom routine:\n",
      "112 ms ± 1.52 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)\n"
     ]
    }
   ],
   "source": [
    "print(\"NumPy routine:\")\n",
    "%timeit counts, edges = np.histogram(x, bins)\n",
    "print(\"Custom routine:\")\n",
    "%timeit np.add.at(counts, np.searchsorted(bins, x), 1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "303eb973",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "NumPy routine:\n"
     ]
    }
   ],
   "source": [
    "x = np.random.randn(1000000)\n",
    "print(\"NumPy routine:\")\n",
    "%timeit counts, edges = np.histogram(x, bins)\n",
    "print(\"Custom routine:\")\n",
    "%timeit np.add.at(counts, np.searchsorted(bins, x), 1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a5f734a7",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
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
   "version": "3.9.13"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
