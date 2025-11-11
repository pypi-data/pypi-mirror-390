{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "169e80fc",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Requirement already satisfied: numpy in c:\\users\\lap-01\\anaconda3\\lib\\site-packages (1.21.5)\n",
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "pip install numpy"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "94111d0c",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "10326722",
   "metadata": {},
   "outputs": [],
   "source": [
    "# NumPy Array A-dimensional arrayttributes\n",
    "import numpy as np\n",
    "np.random.seed(0) # seed for reproducibility\n",
    "x1 = np.random.randint(10, size=6) # One-dimensional array\n",
    "x2 = np.random.randint(10, size=(3, 4)) # Two-dimensional array\n",
    "x3 = np.random.randint(10, size=(3, 4, 5)) # Three-dimensional array"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "3a4b0eee",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "x3 ndim:  3\n",
      "x3 shape: (3, 4, 5)\n",
      "x3 size:  60\n"
     ]
    }
   ],
   "source": [
    "print(\"x3 ndim: \", x3.ndim)\n",
    "print(\"x3 shape:\", x3.shape)\n",
    "print(\"x3 size: \", x3.size)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "ed81bf92",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "dtype: int32\n",
      "itemsize: 4 bytes\n",
      "nbytes: 240 bytes\n"
     ]
    }
   ],
   "source": [
    "print(\"dtype:\", x3.dtype)\n",
    "print(\"itemsize:\", x3.itemsize, \"bytes\")\n",
    "print(\"nbytes:\", x3.nbytes, \"bytes\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "0c7f7ad8",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([5, 0, 3, 3, 7, 9])"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Array Indexing: Accessing Single Elements\n",
    "x1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "feda5fdb",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "5"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x1[0]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "b222c117",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "7"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x1[4]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "c9828983",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "9"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x1[-1]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "62a862d4",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "7"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x1[-2]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "a038d188",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[3, 5, 2, 4],\n",
       "       [7, 6, 8, 8],\n",
       "       [1, 6, 7, 7]])"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "cca28148",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "3"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2[0, 0]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "26e981f4",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2[2, 0]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "f37337e2",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "7"
      ]
     },
     "execution_count": 16,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2[2, -1]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "1f4168ce",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[12,  5,  2,  4],\n",
       "       [ 7,  6,  8,  8],\n",
       "       [ 1,  6,  7,  7]])"
      ]
     },
     "execution_count": 17,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2[0, 0] = 12\n",
    "x2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "9ae4e924",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])"
      ]
     },
     "execution_count": 18,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Array Slicing: Accessing Subarrays\n",
    "x = np.arange(10)\n",
    "x"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "ab2d6c83",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([0, 1, 2, 3, 4])"
      ]
     },
     "execution_count": 19,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " # first five elements\n",
    "x[:5]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "c5e4b212",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([5, 6, 7, 8, 9])"
      ]
     },
     "execution_count": 20,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# elements after index 5\n",
    "x[5:] "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "e5be7ef1",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([4, 5, 6])"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# middle subarray\n",
    "x[4:7] "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "93edeaf1",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([0, 2, 4, 6, 8])"
      ]
     },
     "execution_count": 22,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# every other element\n",
    "x[::2] "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "58d6d02a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([1, 3, 5, 7, 9])"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# every other element, starting at index 1\n",
    "x[1::2]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "cd7cec10",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([9, 8, 7, 6, 5, 4, 3, 2, 1, 0])"
      ]
     },
     "execution_count": 25,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x[::-1] # all elements, reversed"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "53a4bd27",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[12,  5,  2,  4],\n",
       "       [ 7,  6,  8,  8],\n",
       "       [ 1,  6,  7,  7]])"
      ]
     },
     "execution_count": 26,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Multidimensional Arrays\n",
    "x2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "7eb3736f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[12,  5,  2],\n",
       "       [ 7,  6,  8]])"
      ]
     },
     "execution_count": 27,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2[:2, :3] # two rows, three columns"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "adb40ab1",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[12,  2],\n",
       "       [ 7,  8],\n",
       "       [ 1,  7]])"
      ]
     },
     "execution_count": 28,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2[:3, ::2] # all rows, every other column"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "d4facc1d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 7,  7,  6,  1],\n",
       "       [ 8,  8,  6,  7],\n",
       "       [ 4,  2,  5, 12]])"
      ]
     },
     "execution_count": 29,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x2[::-1, ::-1]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "fa0f7197",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[12  7  1]\n"
     ]
    }
   ],
   "source": [
    "#Accessing array rows and columns\n",
    "print(x2[:, 0]) # first column of x2\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "70f1b70c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[12  5  2  4]\n"
     ]
    }
   ],
   "source": [
    "print(x2[0, :]) # first row of x2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "id": "a21c6589",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[12  5  2  4]\n"
     ]
    }
   ],
   "source": [
    " print(x2[0]) # equivalent to x2[0, :]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "id": "17385960",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[12  5  2  4]\n",
      " [ 7  6  8  8]\n",
      " [ 1  6  7  7]]\n"
     ]
    }
   ],
   "source": [
    "#Subarrays as no-copy views\n",
    "print(x2)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "6c0e4f3e",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[12  5]\n",
      " [ 7  6]]\n"
     ]
    }
   ],
   "source": [
    "x2_sub = x2[:2, :2]\n",
    "print(x2_sub)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "7e38fa6f",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[99  5]\n",
      " [ 7  6]]\n"
     ]
    }
   ],
   "source": [
    "x2_sub[0, 0] = 99\n",
    "print(x2_sub)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "id": "3e7b4b73",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[99  5  2  4]\n",
      " [ 7  6  8  8]\n",
      " [ 1  6  7  7]]\n"
     ]
    }
   ],
   "source": [
    "print(x2)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "id": "1521ac1f",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[99  5]\n",
      " [ 7  6]]\n"
     ]
    }
   ],
   "source": [
    "#Creating copies of arrays\n",
    "x2_sub_copy = x2[:2, :2].copy()\n",
    "print(x2_sub_copy)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "id": "3bfc6db8",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[42  5]\n",
      " [ 7  6]]\n"
     ]
    }
   ],
   "source": [
    "x2_sub_copy[0, 0] = 42\n",
    "print(x2_sub_copy)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "id": "80e6304d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[99  5  2  4]\n",
      " [ 7  6  8  8]\n",
      " [ 1  6  7  7]]\n"
     ]
    }
   ],
   "source": [
    "print(x2)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "id": "a02b6581",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[1 2 3]\n",
      " [4 5 6]\n",
      " [7 8 9]]\n"
     ]
    }
   ],
   "source": [
    "#Reshaping of Arrays\n",
    "grid = np.arange(1, 10).reshape((3, 3))\n",
    "print(grid)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "id": "b6d34dc4",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1, 2, 3]])"
      ]
     },
     "execution_count": 41,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x = np.array([1, 2, 3])\n",
    "# row vector via reshape\n",
    "x.reshape((1, 3))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "id": "45f902e0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1, 2, 3]])"
      ]
     },
     "execution_count": 43,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# row vector via newaxis\n",
    "x[np.newaxis, :]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "id": "7d3e80a5",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1],\n",
       "       [2],\n",
       "       [3]])"
      ]
     },
     "execution_count": 44,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# column vector via reshape\n",
    "x.reshape((3, 1))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "id": "0a7a6e97",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1],\n",
       "       [2],\n",
       "       [3]])"
      ]
     },
     "execution_count": 45,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# column vector via newaxis\n",
    "x[:, np.newaxis]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "id": "a8931161",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([1, 2, 3, 3, 2, 1])"
      ]
     },
     "execution_count": 46,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Array Concatenation and Splitting\n",
    "#Concatenation of arrays\n",
    "x = np.array([1, 2, 3])\n",
    "y = np.array([3, 2, 1])\n",
    "np.concatenate([x, y])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "id": "a3d639da",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[ 1  2  3  3  2  1 99 99 99]\n"
     ]
    }
   ],
   "source": [
    "z = [99, 99, 99]\n",
    "print(np.concatenate([x, y, z]))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "id": "d224be9a",
   "metadata": {},
   "outputs": [],
   "source": [
    "grid = np.array([[1, 2, 3],\n",
    "[4, 5, 6]])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "id": "164ae8ea",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1, 2, 3],\n",
       "       [4, 5, 6],\n",
       "       [1, 2, 3],\n",
       "       [4, 5, 6]])"
      ]
     },
     "execution_count": 49,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# concatenate along the first axis\n",
    "np.concatenate([grid, grid])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "id": "8965119f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1, 2, 3, 1, 2, 3],\n",
       "       [4, 5, 6, 4, 5, 6]])"
      ]
     },
     "execution_count": 50,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# concatenate along the second axis (zero-indexed)\n",
    "np.concatenate([grid, grid], axis=1)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "id": "d79b7ba6",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1, 2, 3],\n",
       "       [9, 8, 7],\n",
       "       [6, 5, 4]])"
      ]
     },
     "execution_count": 51,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x = np.array([1, 2, 3])\n",
    "grid = np.array([[9, 8, 7],\n",
    "                 [6, 5, 4]])\n",
    "# vertically stack the arrays\n",
    "np.vstack([x, grid])\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "id": "f241b0c1",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 9,  8,  7, 99],\n",
       "       [ 6,  5,  4, 99]])"
      ]
     },
     "execution_count": 52,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# horizontally stack the arrays\n",
    "y = np.array([[99],\n",
    "             [99]])\n",
    "np.hstack([grid, y])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "id": "06bb0fec",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[1 2 3] [99 99] [3 2 1]\n"
     ]
    }
   ],
   "source": [
    "#Splitting of arrays\n",
    "x = [1, 2, 3, 99, 99, 3, 2, 1]\n",
    "x1, x2, x3 = np.split(x, [3, 5])\n",
    "print(x1, x2, x3)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "id": "701312e9",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 0,  1,  2,  3],\n",
       "       [ 4,  5,  6,  7],\n",
       "       [ 8,  9, 10, 11],\n",
       "       [12, 13, 14, 15]])"
      ]
     },
     "execution_count": 54,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "grid = np.arange(16).reshape((4, 4))\n",
    "grid"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 55,
   "id": "976b4aef",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[0 1 2 3]\n",
      " [4 5 6 7]]\n",
      "[[ 8  9 10 11]\n",
      " [12 13 14 15]]\n"
     ]
    }
   ],
   "source": [
    "upper, lower = np.vsplit(grid, [2])\n",
    "print(upper)\n",
    "print(lower)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 56,
   "id": "3e4cdfb1",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[[ 0  1]\n",
      " [ 4  5]\n",
      " [ 8  9]\n",
      " [12 13]]\n",
      "[[ 2  3]\n",
      " [ 6  7]\n",
      " [10 11]\n",
      " [14 15]]\n"
     ]
    }
   ],
   "source": [
    "left, right = np.hsplit(grid, [2])\n",
    "print(left)\n",
    "print(right)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "11232c91",
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
