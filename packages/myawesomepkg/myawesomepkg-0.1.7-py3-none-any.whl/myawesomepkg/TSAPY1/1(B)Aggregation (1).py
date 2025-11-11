{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "b1716d12-c5e2-43e6-a9b2-23fdab9b64d6",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "ff55f097-4d1c-4289-98dd-c65faad54cd0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "52.74561706217718"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "L = np.random.random(100)\n",
    "sum(L)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "39f25dea-4547-48e5-b46a-4fbe67945454",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "52.74561706217718"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.sum(L)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "7da5f038-28ee-4a98-a702-042c8d0b5e1a",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "112 ms ± 31.8 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)\n",
      "1.08 ms ± 49 µs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)\n"
     ]
    }
   ],
   "source": [
    "big_array = np.random.rand(1000000)\n",
    "%timeit sum(big_array)\n",
    "%timeit np.sum(big_array)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "6d945538-3f7a-48f7-8308-ddc0118ef92e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(2.459947670896412e-06, 0.9999994968740656)"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "min(big_array), max(big_array)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "6340e901-30d7-4a36-9421-ba0f87e64969",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(2.459947670896412e-06, 0.9999994968740656)"
      ]
     },
     "execution_count": 16,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.min(big_array), np.max(big_array)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "2c837204-ddd6-4206-99d3-e2dc356f92ba",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[0.40515773 0.12656963 0.14937442 0.00683728]\n",
      " [0.3502941  0.62659932 0.54795217 0.13145624]\n",
      " [0.05532995 0.49480523 0.77369714 0.42759192]]\n"
     ]
    }
   ],
   "source": [
    " M = np.random.random((3, 4))\n",
    " print(M)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "973947a3-609a-4883-abe8-c2f044c9b78a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "4.095665116718065"
      ]
     },
     "execution_count": 18,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M.sum()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "87d935f2-b8f9-46f5-bea8-8bab6a4efeef",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([0.05532995, 0.12656963, 0.14937442, 0.00683728])"
      ]
     },
     "execution_count": 19,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M.min(axis=0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "65bb11eb-5b50-497b-bd83-bd4a2a81e00e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([0.40515773, 0.62659932, 0.77369714])"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M.max(axis=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "ea408e7d-6c3a-4071-a7ef-aaa51e67bfe5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[189 170 189 163 183 171 185 168 173 183 173 173 175 178 183 193 178 173\n",
      " 174 183 183 168 170 178 182 180 183 178 182 188 175 179 183 193 182 183\n",
      " 177 185 188 188 182 185]\n"
     ]
    }
   ],
   "source": [
    "import pandas as pd\n",
    "data = pd.read_csv(\"D:\\\\Data\\\\president_heights.csv\")\n",
    "heights = np.array(data['height(cm)'])\n",
    "print(heights)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "74c0b07a-e2dd-4697-89e3-0c307106dd32",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Mean height:        179.73809523809524\n",
      "Standard deviation: 6.931843442745892\n",
      "Minimum height:     163\n",
      "Maximum height:     193\n"
     ]
    }
   ],
   "source": [
    " print(\"Mean height:       \", heights.mean())\n",
    " print(\"Standard deviation:\", heights.std())\n",
    " print(\"Minimum height:    \", heights.min())\n",
    " print(\"Maximum height:    \", heights.max())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "id": "48d75be2-f202-4b67-8f70-ec2c0b2b4139",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "25th percentile:    174.25\n",
      "Median:             182.0\n",
      "75th percentile:    183.0\n"
     ]
    }
   ],
   "source": [
    "print(\"25th percentile:   \", np.percentile(heights, 25))\n",
    "print(\"Median:            \", np.median(heights))\n",
    "print(\"75th percentile:   \", np.percentile(heights, 75))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "id": "f9b51dce-4595-4bc2-8bd0-0aba2df203d4",
   "metadata": {},
   "outputs": [],
   "source": [
    "%matplotlib inline\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn; seaborn.set()  # set plot style"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fb31754c-62a9-4887-8552-8b7940135557",
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.hist(heights)\n",
    "plt.title('Height Distribution of US Presidents')\n",
    "        plt.xlabel('height (cm)')\n",
    "        plt.ylabel('number');\n"
   ]
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
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
