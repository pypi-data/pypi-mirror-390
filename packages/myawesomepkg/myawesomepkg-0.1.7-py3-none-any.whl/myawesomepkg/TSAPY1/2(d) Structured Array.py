{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "a48de104",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "2a44575b",
   "metadata": {},
   "outputs": [],
   "source": [
    "name = ['Alice', 'Bob', 'Cathy', 'Doug']\n",
    "age = [25, 45, 37, 19]\n",
    "weight = [55.0, 85.5, 68.0, 61.5]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "98f8f978",
   "metadata": {},
   "outputs": [],
   "source": [
    "x = np.zeros(4, dtype=int)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "62710353",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[('name', '<U10'), ('age', '<i4'), ('weight', '<f8')]\n"
     ]
    }
   ],
   "source": [
    "# Use a compound data type for structured arrays\n",
    "data = np.zeros(4, dtype={'names':('name', 'age', 'weight'), 'formats':('U10', 'i4', 'f8')})\n",
    "print(data.dtype)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "75429517",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[('Alice', 25, 55. ) ('Bob', 45, 85.5) ('Cathy', 37, 68. )\n",
      " ('Doug', 19, 61.5)]\n"
     ]
    }
   ],
   "source": [
    "data['name'] = name\n",
    "data['age'] = age\n",
    "data['weight'] = weight\n",
    "print(data)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "81014a71",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array(['Alice', 'Bob', 'Cathy', 'Doug'], dtype='<U10')"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Get all names\n",
    "data['name']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "4ab9cc78",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "('Alice', 25, 55.)"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Get first row of data\n",
    "data[0]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "97e72108",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'Doug'"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Get the name from the last row\n",
    "data[-1]['name']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "f766b733",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array(['Alice', 'Doug'], dtype='<U10')"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Get names where age is under 30\n",
    "data[data['age'] < 30]['name']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "97755d62",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "dtype([('name', '<U10'), ('age', '<i4'), ('weight', '<f8')])"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Creating Structured Arrays\n",
    "np.dtype({'names':('name', 'age', 'weight'), 'formats':('U10', 'i4', 'f8')})\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "42dc0929",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "dtype([('name', 'S10'), ('age', '<i4'), ('weight', '<f8')])"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dtype([('name', 'S10'), ('age', 'i4'), ('weight', 'f8')])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "49dba453",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "dtype([('f0', 'S10'), ('f1', '<i4'), ('f2', '<f8')])"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dtype('S10,i4,f8')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "322c3d0b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "(0, [[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])\n",
      "[[0. 0. 0.]\n",
      " [0. 0. 0.]\n",
      " [0. 0. 0.]]\n"
     ]
    }
   ],
   "source": [
    "#More Advanced Compound Types\n",
    "tp = np.dtype([('id', 'i8'), ('mat', 'f8', (3, 3))])\n",
    "X = np.zeros(1, dtype=tp)\n",
    "print(X[0])\n",
    "print(X['mat'][0])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "5f12d9cd",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([25, 45, 37, 19])"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#RecordArrays: Structured Arrays with a Twist\n",
    "data['age']\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "0c450acf",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([25, 45, 37, 19])"
      ]
     },
     "execution_count": 16,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data_rec = data.view(np.recarray)\n",
    "data_rec.age"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "dfb95656",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "141 ns ± 11 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)\n",
      "2.31 µs ± 130 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)\n",
      "3.74 µs ± 171 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)\n"
     ]
    }
   ],
   "source": [
    "%timeit data['age']\n",
    "%timeit data_rec['age']\n",
    "%timeit data_rec.age"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7dfe30fe",
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
