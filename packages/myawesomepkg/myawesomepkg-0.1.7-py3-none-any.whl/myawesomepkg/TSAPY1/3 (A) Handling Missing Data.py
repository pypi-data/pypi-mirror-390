{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "1fd1dba2",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import pandas as pd\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "2b7ac399",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([1, None, 3, 4], dtype=object)"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vals1 = np.array([1, None, 3, 4])\n",
    "vals1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "50393a54",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "dtype = object\n",
      "63.4 ms ± 4.21 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)\n",
      "\n",
      "dtype = int\n",
      "2.24 ms ± 134 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)\n",
      "\n"
     ]
    }
   ],
   "source": [
    "for dtype in ['object', 'int']:\n",
    "    print(\"dtype =\", dtype)\n",
    "    %timeit np.arange(1E6, dtype=dtype).sum()\n",
    "    print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "ef13ae07",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "dtype('float64')"
      ]
     },
     "execution_count": 6,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vals2 = np.array([1, np.nan, 3, 4])\n",
    "vals2.dtype\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "a608bfd2",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "nan"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "1 + np.nan"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "ee1ea156",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "nan"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "0 * np.nan"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "710ab0fa",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(nan, nan, nan)"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vals2.sum(), vals2.min(), vals2.max()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "57cd4e3a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(8.0, 1.0, 4.0)"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.nansum(vals2), np.nanmin(vals2), np.nanmax(vals2)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "648ccea3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    1.0\n",
       "1    NaN\n",
       "2    2.0\n",
       "3    NaN\n",
       "dtype: float64"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.Series([1, np.nan, 2, None])\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "8ecef540",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    0\n",
       "1    1\n",
       "dtype: int32"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x = pd.Series(range(2), dtype=int)\n",
    "x"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "097233c1",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    NaN\n",
       "1    1.0\n",
       "dtype: float64"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x[0] = None\n",
    "x"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "f2b81620",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Detecting null values\n",
    "data = pd.Series([1, np.nan, 'hello', None])\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "11a5c988",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    False\n",
       "1     True\n",
       "2    False\n",
       "3     True\n",
       "dtype: bool"
      ]
     },
     "execution_count": 16,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data.isnull()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "9ecaa9a5",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0        1\n",
       "2    hello\n",
       "dtype: object"
      ]
     },
     "execution_count": 17,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[data.notnull()]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "d7c214eb",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0        1\n",
       "2    hello\n",
       "dtype: object"
      ]
     },
     "execution_count": 18,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Dropping null values\n",
    "data.dropna()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "8d7e21ef",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>0</th>\n",
       "      <th>1</th>\n",
       "      <th>2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2.0</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>NaN</td>\n",
       "      <td>4.0</td>\n",
       "      <td>6</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     0    1  2\n",
       "0  1.0  NaN  2\n",
       "1  2.0  3.0  5\n",
       "2  NaN  4.0  6"
      ]
     },
     "execution_count": 20,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df = pd.DataFrame([[1, np.nan, 2],\n",
    "                  [2, 3, 5],\n",
    "                  [np.nan, 4, 6]])\n",
    "df\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "3355043d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>0</th>\n",
       "      <th>1</th>\n",
       "      <th>2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2.0</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     0    1  2\n",
       "1  2.0  3.0  5"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.dropna()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "c3c7920b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>2</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>6</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   2\n",
       "0  2\n",
       "1  5\n",
       "2  6"
      ]
     },
     "execution_count": 22,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.dropna(axis='columns')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "d987a577",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>0</th>\n",
       "      <th>1</th>\n",
       "      <th>2</th>\n",
       "      <th>3</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2.0</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>NaN</td>\n",
       "      <td>4.0</td>\n",
       "      <td>6</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     0    1  2   3\n",
       "0  1.0  NaN  2 NaN\n",
       "1  2.0  3.0  5 NaN\n",
       "2  NaN  4.0  6 NaN"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df[3] = np.nan\n",
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "5fa2e884",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>0</th>\n",
       "      <th>1</th>\n",
       "      <th>2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2.0</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>NaN</td>\n",
       "      <td>4.0</td>\n",
       "      <td>6</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     0    1  2\n",
       "0  1.0  NaN  2\n",
       "1  2.0  3.0  5\n",
       "2  NaN  4.0  6"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.dropna(axis='columns', how='all')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "2b62a4d7",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>0</th>\n",
       "      <th>1</th>\n",
       "      <th>2</th>\n",
       "      <th>3</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2.0</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     0    1  2   3\n",
       "1  2.0  3.0  5 NaN"
      ]
     },
     "execution_count": 25,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.dropna(axis='rows', thresh=3)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "ab65fccd",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "a    1.0\n",
       "b    NaN\n",
       "c    2.0\n",
       "d    NaN\n",
       "e    3.0\n",
       "dtype: float64"
      ]
     },
     "execution_count": 26,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Filling null values\n",
    "data = pd.Series([1, np.nan, 2, None, 3], index=list('abcde'))\n",
    "data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "79701b50",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "a    1.0\n",
       "b    0.0\n",
       "c    2.0\n",
       "d    0.0\n",
       "e    3.0\n",
       "dtype: float64"
      ]
     },
     "execution_count": 27,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data.fillna(0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "e2920e55",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "a    1.0\n",
       "b    1.0\n",
       "c    2.0\n",
       "d    2.0\n",
       "e    3.0\n",
       "dtype: float64"
      ]
     },
     "execution_count": 28,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# forward-fill\n",
    "data.fillna(method='ffill')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "057ad778",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "a    1.0\n",
       "b    2.0\n",
       "c    2.0\n",
       "d    3.0\n",
       "e    3.0\n",
       "dtype: float64"
      ]
     },
     "execution_count": 30,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# back-fill\n",
    "data.fillna(method='bfill')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "1d99ee5b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>0</th>\n",
       "      <th>1</th>\n",
       "      <th>2</th>\n",
       "      <th>3</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1.0</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2.0</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>NaN</td>\n",
       "      <td>4.0</td>\n",
       "      <td>6</td>\n",
       "      <td>NaN</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     0    1  2   3\n",
       "0  1.0  NaN  2 NaN\n",
       "1  2.0  3.0  5 NaN\n",
       "2  NaN  4.0  6 NaN"
      ]
     },
     "execution_count": 31,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "id": "a5e51c61",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>0</th>\n",
       "      <th>1</th>\n",
       "      <th>2</th>\n",
       "      <th>3</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>1.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>2.0</td>\n",
       "      <td>2.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2.0</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5.0</td>\n",
       "      <td>5.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>NaN</td>\n",
       "      <td>4.0</td>\n",
       "      <td>6.0</td>\n",
       "      <td>6.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     0    1    2    3\n",
       "0  1.0  1.0  2.0  2.0\n",
       "1  2.0  3.0  5.0  5.0\n",
       "2  NaN  4.0  6.0  6.0"
      ]
     },
     "execution_count": 32,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.fillna(method='ffill', axis=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1ae8ebbc",
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
