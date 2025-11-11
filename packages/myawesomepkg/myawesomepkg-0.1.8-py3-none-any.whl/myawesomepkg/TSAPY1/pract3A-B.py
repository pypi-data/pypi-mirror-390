{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "822792da-dbb3-4ec7-a179-480020ac004b",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Missing Data in Pandas\n",
    "import numpy as np\n",
    "import pandas as pd"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "a7aebbf3-0776-4371-9775-aaa82496ac2a",
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
   "execution_count": 3,
   "id": "42e9d234-98ea-40ef-b808-e149dec83b46",
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
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Detecting null values\n",
    "data = pd.Series([1, np.nan, 'hello', None])\n",
    "data.isnull()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "d6078385-1b04-4c3b-b3c2-1f0cc7219a33",
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
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[data.notnull()]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "26ed180e-d636-4eda-bb6c-6aef597e3189",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "dtype = object\n",
      "120 ms ± 21.6 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)\n",
      "\n",
      "dtype = int\n",
      "5.37 ms ± 184 μs per loop (mean ± std. dev. of 7 runs, 100 loops each)\n",
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
   "execution_count": 7,
   "id": "60a94109-d9bc-4781-9ef5-152f458c9133",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "30.0\n"
     ]
    }
   ],
   "source": [
    "vals1 = np.array([10, 20, np.nan])\n",
    "print(np.nansum(vals1))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "29e48dea-555c-4a3a-b7d1-6af63234b7a9",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "dtype('float64')"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vals2 = np.array([1, np.nan, 3, 4])\n",
    "vals2.dtype"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "1c9053b8-8790-4bc8-b8f5-7617a1248b5e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "nan"
      ]
     },
     "execution_count": 9,
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
   "execution_count": 10,
   "id": "4d26e974-d2f9-4aef-bf09-0961429ff7e0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "nan"
      ]
     },
     "execution_count": 10,
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
   "execution_count": 11,
   "id": "ad69d303-24af-4718-8a99-2a063abaa8ce",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(np.float64(nan), np.float64(nan), np.float64(nan))"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vals2.sum(), vals2.min(), vals2.max()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "ae143434-f619-46cd-a43e-ff5a7daf2a28",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(np.float64(8.0), np.float64(1.0), np.float64(4.0))"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.nansum(vals2), np.nanmin(vals2), np.nanmax(vals2)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "8533305f-78e0-4c3a-b122-23be6b5f73b4",
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
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.Series([1, np.nan, 2, None])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "5317b0d7-a933-4b22-81d6-2fa38a853d5d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    0\n",
       "1    1\n",
       "dtype: int64"
      ]
     },
     "execution_count": 14,
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
   "execution_count": 15,
   "id": "10c2aa25-109e-4678-9f17-82965c0d8d2d",
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
     "execution_count": 15,
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
   "execution_count": 16,
   "id": "97a73881-49ba-445a-b0f2-670a03f9b562",
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
    "data = pd.Series([1, np.nan, 'hello', None])\n",
    "data.isnull()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "62c1d7ce-93e6-4fb2-acb2-ecc606a3b14d",
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
    "data[data.notnull()]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "ccdd04f5-7093-4761-97ed-523295ac42f5",
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
    "data.dropna()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "8411cb90-03c7-4c26-9fe9-d81b996d45cb",
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
     "execution_count": 19,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df = pd.DataFrame([[1, np.nan, 2],\n",
    "[2, 3, 5],\n",
    "[np.nan, 4, 6]])\n",
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "db960192-bdc5-4ca1-8b25-d15a75038c09",
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
     "execution_count": 20,
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
   "execution_count": 21,
   "id": "192591c6-cdf0-4d9b-9974-ecd6313b7a13",
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
     "execution_count": 21,
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
   "execution_count": 22,
   "id": "7f404f2c-7825-4be1-9df0-6af94dc64127",
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
     "execution_count": 22,
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
   "execution_count": 23,
   "id": "bce0355e-bf7a-488b-9b83-7d8d3d6d11d1",
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
     "execution_count": 23,
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
   "execution_count": 24,
   "id": "c1c69f9f-84d9-4259-9b82-bf19948374b0",
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
     "execution_count": 24,
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
   "execution_count": 25,
   "id": "02274d77-117a-4346-b0cd-25a11e195ea1",
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
     "execution_count": 25,
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
   "execution_count": 26,
   "id": "ff7c66b4-8886-4d12-82a9-e033e13bf3f9",
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
     "execution_count": 26,
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
   "execution_count": 27,
   "id": "855559ab-1428-4555-a2b0-6818f0e4be25",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_18940\\3316037056.py:2: FutureWarning: Series.fillna with 'method' is deprecated and will raise in a future version. Use obj.ffill() or obj.bfill() instead.\n",
      "  data.fillna(method='ffill')\n"
     ]
    },
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
     "execution_count": 27,
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
   "execution_count": 28,
   "id": "cf65f8ea-cce8-4198-bce6-665ade36070c",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_18940\\2650514875.py:2: FutureWarning: Series.fillna with 'method' is deprecated and will raise in a future version. Use obj.ffill() or obj.bfill() instead.\n",
      "  data.fillna(method='bfill')\n"
     ]
    },
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
     "execution_count": 28,
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
   "execution_count": 29,
   "id": "242b6c7a-20b1-45ae-bcb4-f898d0f60213",
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
     "execution_count": 29,
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
   "execution_count": 30,
   "id": "fab1a27d-5762-4c61-ba7f-57eeb9577b99",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_18940\\3455056665.py:1: FutureWarning: DataFrame.fillna with 'method' is deprecated and will raise in a future version. Use obj.ffill() or obj.bfill() instead.\n",
      "  df.fillna(method='ffill', axis=1)\n"
     ]
    },
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
     "execution_count": 30,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "\n",
    "df.fillna(method='ffill', axis=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "721bd85e-4b3e-4b34-bcfc-ccc683be017c",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(California, 2000)    33871648\n",
       "(California, 2010)    37253956\n",
       "(New York, 2000)      18976457\n",
       "(New York, 2010)      19378102\n",
       "(Texas, 2000)         20851820\n",
       "(Texas, 2010)         25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 31,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "index = [('California', 2000), ('California', 2010),\n",
    "('New York', 2000), ('New York', 2010),\n",
    "('Texas', 2000), ('Texas', 2010)]\n",
    "populations = [33871648, 37253956,\n",
    "18976457, 19378102,\n",
    "20851820, 25145561]\n",
    "pop = pd.Series(populations, index=index)\n",
    "pop"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "id": "cd4522c5-a2de-473a-a2e0-509485b3941a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(California, 2010)    37253956\n",
       "(New York, 2000)      18976457\n",
       "(New York, 2010)      19378102\n",
       "(Texas, 2000)         20851820\n",
       "dtype: int64"
      ]
     },
     "execution_count": 32,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop[('California', 2010):('Texas', 2000)]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "id": "f42bb21b-6345-4084-a210-fa6464c084a4",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "MultiIndex([('California', 2000),\n",
       "            ('California', 2010),\n",
       "            (  'New York', 2000),\n",
       "            (  'New York', 2010),\n",
       "            (     'Texas', 2000),\n",
       "            (     'Texas', 2010)],\n",
       "           )"
      ]
     },
     "execution_count": 33,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "index = pd.MultiIndex.from_tuples(index)\n",
    "index"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "e1129e15-b746-4822-8f82-e95c1943fef5",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "New York    2000    18976457\n",
       "            2010    19378102\n",
       "Texas       2000    20851820\n",
       "            2010    25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 34,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop = pop.reindex(index)\n",
    "pop"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "c8e3ab93-a611-48de-b950-517b9b3af9ed",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "California    37253956\n",
       "New York      19378102\n",
       "Texas         25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 35,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop[:, 2010]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "id": "cd13cdf1-25f0-4663-833a-210d91a985db",
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
       "      <th>2000</th>\n",
       "      <th>2010</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>California</th>\n",
       "      <td>33871648</td>\n",
       "      <td>37253956</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>New York</th>\n",
       "      <td>18976457</td>\n",
       "      <td>19378102</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Texas</th>\n",
       "      <td>20851820</td>\n",
       "      <td>25145561</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                2000      2010\n",
       "California  33871648  37253956\n",
       "New York    18976457  19378102\n",
       "Texas       20851820  25145561"
      ]
     },
     "execution_count": 36,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop_df = pop.unstack()\n",
    "pop_df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "id": "9155ecaf-2a85-4731-8f71-0353eb83a3fb",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "New York    2000    18976457\n",
       "            2010    19378102\n",
       "Texas       2000    20851820\n",
       "            2010    25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 37,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop_df.stack()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "id": "6be0213d-b75a-49fc-846b-082cf43be9e9",
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
       "      <th></th>\n",
       "      <th>total</th>\n",
       "      <th>under18</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">California</th>\n",
       "      <th>2000</th>\n",
       "      <td>33871648</td>\n",
       "      <td>9267089</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2010</th>\n",
       "      <td>37253956</td>\n",
       "      <td>9284094</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">New York</th>\n",
       "      <th>2000</th>\n",
       "      <td>18976457</td>\n",
       "      <td>4687374</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2010</th>\n",
       "      <td>19378102</td>\n",
       "      <td>4318033</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">Texas</th>\n",
       "      <th>2000</th>\n",
       "      <td>20851820</td>\n",
       "      <td>5906301</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2010</th>\n",
       "      <td>25145561</td>\n",
       "      <td>6879014</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                    total  under18\n",
       "California 2000  33871648  9267089\n",
       "           2010  37253956  9284094\n",
       "New York   2000  18976457  4687374\n",
       "           2010  19378102  4318033\n",
       "Texas      2000  20851820  5906301\n",
       "           2010  25145561  6879014"
      ]
     },
     "execution_count": 38,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop_df = pd.DataFrame({'total': pop,\n",
    "'under18': [9267089, 9284094,\n",
    "4687374, 4318033,\n",
    "5906301, 6879014]})\n",
    "pop_df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "id": "37df56a1-bbb4-46aa-8508-e32a3e65304a",
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
       "      <th>2000</th>\n",
       "      <th>2010</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>California</th>\n",
       "      <td>0.273594</td>\n",
       "      <td>0.249211</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>New York</th>\n",
       "      <td>0.247010</td>\n",
       "      <td>0.222831</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Texas</th>\n",
       "      <td>0.283251</td>\n",
       "      <td>0.273568</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                2000      2010\n",
       "California  0.273594  0.249211\n",
       "New York    0.247010  0.222831\n",
       "Texas       0.283251  0.273568"
      ]
     },
     "execution_count": 39,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "f_u18 = pop_df['under18'] / pop_df['total']\n",
    "f_u18.unstack()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "id": "84c056c9-db9d-4f1c-bbe9-73770c491c33",
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
       "      <th></th>\n",
       "      <th>data1</th>\n",
       "      <th>data2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">a</th>\n",
       "      <th>1</th>\n",
       "      <td>0.478627</td>\n",
       "      <td>0.628762</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>0.327155</td>\n",
       "      <td>0.747383</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">b</th>\n",
       "      <th>1</th>\n",
       "      <td>0.997522</td>\n",
       "      <td>0.443755</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>0.428418</td>\n",
       "      <td>0.415810</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "        data1     data2\n",
       "a 1  0.478627  0.628762\n",
       "  2  0.327155  0.747383\n",
       "b 1  0.997522  0.443755\n",
       "  2  0.428418  0.415810"
      ]
     },
     "execution_count": 40,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df = pd.DataFrame(np.random.rand(4, 2),\n",
    "index=[['a', 'a', 'b', 'b'], [1, 2, 1, 2]],\n",
    "columns=['data1', 'data2'])\n",
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "id": "87b94068-cad8-47df-a350-e67d083d60cd",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "Texas       2000    20851820\n",
       "            2010    25145561\n",
       "New York    2000    18976457\n",
       "            2010    19378102\n",
       "dtype: int64"
      ]
     },
     "execution_count": 41,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data = {('California', 2000): 33871648,\n",
    "('California', 2010): 37253956,\n",
    "('Texas', 2000): 20851820,\n",
    "('Texas', 2010): 25145561,\n",
    "('New York', 2000): 18976457,\n",
    "('New York', 2010): 19378102}\n",
    "pd.Series(data)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "id": "2357c39e-189d-49d8-a652-0cc60fd0549d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "MultiIndex([('a', 1),\n",
       "            ('a', 2),\n",
       "            ('b', 1),\n",
       "            ('b', 2)],\n",
       "           )"
      ]
     },
     "execution_count": 42,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.MultiIndex.from_arrays([['a', 'a', 'b', 'b'], [1, 2, 1, 2]])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "id": "1dc18ebb-fe8a-4bac-9fbf-ea38e7d11e16",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "MultiIndex([('a', 1),\n",
       "            ('a', 2),\n",
       "            ('b', 1),\n",
       "            ('b', 2)],\n",
       "           )"
      ]
     },
     "execution_count": 43,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.MultiIndex.from_tuples([('a', 1), ('a', 2), ('b', 1), ('b', 2)])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "id": "13bff348-d67d-49ba-b16c-16f31032c1f2",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "MultiIndex([('a', 1),\n",
       "            ('a', 2),\n",
       "            ('b', 1),\n",
       "            ('b', 2)],\n",
       "           )"
      ]
     },
     "execution_count": 44,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.MultiIndex.from_product([['a', 'b'], [1, 2]])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "id": "7ce4bd44-6979-4413-84cd-6195fd5440d1",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "MultiIndex([('a', 1),\n",
       "            ('a', 2),\n",
       "            ('b', 1),\n",
       "            ('b', 2)],\n",
       "           )"
      ]
     },
     "execution_count": 45,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.MultiIndex(levels=[['a', 'b'], [1, 2]],\n",
    "              codes=[[0, 0, 1, 1], [0, 1, 0, 1]])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "id": "745e2c13-b099-4901-b277-074796dcd5b0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "state       year\n",
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "New York    2000    18976457\n",
       "            2010    19378102\n",
       "Texas       2000    20851820\n",
       "            2010    25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 46,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop.index.names = ['state', 'year']\n",
    "pop"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "id": "0676dea4-4f80-4165-81ea-3869b9ab1f15",
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
       "    .dataframe thead tr th {\n",
       "        text-align: left;\n",
       "    }\n",
       "\n",
       "    .dataframe thead tr:last-of-type th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>subject</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Bob</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Guido</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Sue</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th>visit</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2013</th>\n",
       "      <th>1</th>\n",
       "      <td>49.0</td>\n",
       "      <td>38.5</td>\n",
       "      <td>37.0</td>\n",
       "      <td>38.2</td>\n",
       "      <td>33.0</td>\n",
       "      <td>38.3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>43.0</td>\n",
       "      <td>38.6</td>\n",
       "      <td>23.0</td>\n",
       "      <td>37.5</td>\n",
       "      <td>42.0</td>\n",
       "      <td>35.2</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2014</th>\n",
       "      <th>1</th>\n",
       "      <td>22.0</td>\n",
       "      <td>37.3</td>\n",
       "      <td>46.0</td>\n",
       "      <td>36.5</td>\n",
       "      <td>35.0</td>\n",
       "      <td>37.3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>40.0</td>\n",
       "      <td>36.9</td>\n",
       "      <td>58.0</td>\n",
       "      <td>37.1</td>\n",
       "      <td>48.0</td>\n",
       "      <td>35.8</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "subject      Bob       Guido         Sue      \n",
       "type          HR  Temp    HR  Temp    HR  Temp\n",
       "year visit                                    \n",
       "2013 1      49.0  38.5  37.0  38.2  33.0  38.3\n",
       "     2      43.0  38.6  23.0  37.5  42.0  35.2\n",
       "2014 1      22.0  37.3  46.0  36.5  35.0  37.3\n",
       "     2      40.0  36.9  58.0  37.1  48.0  35.8"
      ]
     },
     "execution_count": 47,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "index = pd.MultiIndex.from_product([[2013, 2014], [1, 2]],\n",
    "names=['year', 'visit'])\n",
    "columns = pd.MultiIndex.from_product([['Bob', 'Guido', 'Sue'], ['HR', 'Temp']],\n",
    "names=['subject', 'type'])\n",
    "\n",
    "data = np.round(np.random.randn(4, 6), 1)\n",
    "data[:, ::2] *= 10\n",
    "data += 37\n",
    "\n",
    "health_data = pd.DataFrame(data, index=index, columns=columns)\n",
    "health_data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "id": "93319435-e56e-4939-b56c-eb8b3bd97163",
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
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th>visit</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2013</th>\n",
       "      <th>1</th>\n",
       "      <td>37.0</td>\n",
       "      <td>38.2</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>23.0</td>\n",
       "      <td>37.5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2014</th>\n",
       "      <th>1</th>\n",
       "      <td>46.0</td>\n",
       "      <td>36.5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>58.0</td>\n",
       "      <td>37.1</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "type          HR  Temp\n",
       "year visit            \n",
       "2013 1      37.0  38.2\n",
       "     2      23.0  37.5\n",
       "2014 1      46.0  36.5\n",
       "     2      58.0  37.1"
      ]
     },
     "execution_count": 48,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "health_data['Guido']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "id": "aa5d6ddb-581f-4d7e-b148-602f94749e1b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "state       year\n",
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "New York    2000    18976457\n",
       "            2010    19378102\n",
       "Texas       2000    20851820\n",
       "            2010    25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 49,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "id": "6e2a0550-b4f7-4e1a-9c9e-e6a537554179",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "np.int64(33871648)"
      ]
     },
     "execution_count": 50,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop['California', 2000]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "id": "d07b7114-56b8-4609-b749-c1e0c8c9fa64",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "year\n",
       "2000    33871648\n",
       "2010    37253956\n",
       "dtype: int64"
      ]
     },
     "execution_count": 51,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop['California']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "id": "be5249e4-9244-4145-82a9-6ead97ef95ec",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "state       year\n",
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "New York    2000    18976457\n",
       "            2010    19378102\n",
       "dtype: int64"
      ]
     },
     "execution_count": 52,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop.loc['California':'New York']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "id": "3f02298e-195e-4f18-a8c6-5352e1fc5c14",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "state\n",
       "California    33871648\n",
       "New York      18976457\n",
       "Texas         20851820\n",
       "dtype: int64"
      ]
     },
     "execution_count": 53,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop[:, 2000]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "id": "a95754cd-af47-42df-b021-4a3f7acf8be0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "state       year\n",
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "Texas       2010    25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 54,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop[pop > 22000000]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 55,
   "id": "ca7b8ea9-951b-46e5-bebf-d47ac2f15bf3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "state       year\n",
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "Texas       2000    20851820\n",
       "            2010    25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 55,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop[['California', 'Texas']]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 56,
   "id": "3aefb9d1-98c2-4749-b926-a4691b41de28",
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
       "    .dataframe thead tr th {\n",
       "        text-align: left;\n",
       "    }\n",
       "\n",
       "    .dataframe thead tr:last-of-type th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>subject</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Bob</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Guido</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Sue</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th>visit</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2013</th>\n",
       "      <th>1</th>\n",
       "      <td>49.0</td>\n",
       "      <td>38.5</td>\n",
       "      <td>37.0</td>\n",
       "      <td>38.2</td>\n",
       "      <td>33.0</td>\n",
       "      <td>38.3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>43.0</td>\n",
       "      <td>38.6</td>\n",
       "      <td>23.0</td>\n",
       "      <td>37.5</td>\n",
       "      <td>42.0</td>\n",
       "      <td>35.2</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2014</th>\n",
       "      <th>1</th>\n",
       "      <td>22.0</td>\n",
       "      <td>37.3</td>\n",
       "      <td>46.0</td>\n",
       "      <td>36.5</td>\n",
       "      <td>35.0</td>\n",
       "      <td>37.3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>40.0</td>\n",
       "      <td>36.9</td>\n",
       "      <td>58.0</td>\n",
       "      <td>37.1</td>\n",
       "      <td>48.0</td>\n",
       "      <td>35.8</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "subject      Bob       Guido         Sue      \n",
       "type          HR  Temp    HR  Temp    HR  Temp\n",
       "year visit                                    \n",
       "2013 1      49.0  38.5  37.0  38.2  33.0  38.3\n",
       "     2      43.0  38.6  23.0  37.5  42.0  35.2\n",
       "2014 1      22.0  37.3  46.0  36.5  35.0  37.3\n",
       "     2      40.0  36.9  58.0  37.1  48.0  35.8"
      ]
     },
     "execution_count": 56,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "health_data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 57,
   "id": "c7d0357c-1b12-4eed-8bb9-4f689921749e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "year  visit\n",
       "2013  1        37.0\n",
       "      2        23.0\n",
       "2014  1        46.0\n",
       "      2        58.0\n",
       "Name: (Guido, HR), dtype: float64"
      ]
     },
     "execution_count": 57,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "health_data['Guido', 'HR']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 58,
   "id": "78e41138-b1f1-45de-9fd5-5d4e2434e5da",
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
       "    .dataframe thead tr th {\n",
       "        text-align: left;\n",
       "    }\n",
       "\n",
       "    .dataframe thead tr:last-of-type th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>subject</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Bob</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th>visit</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2013</th>\n",
       "      <th>1</th>\n",
       "      <td>49.0</td>\n",
       "      <td>38.5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>43.0</td>\n",
       "      <td>38.6</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "subject      Bob      \n",
       "type          HR  Temp\n",
       "year visit            \n",
       "2013 1      49.0  38.5\n",
       "     2      43.0  38.6"
      ]
     },
     "execution_count": 58,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "health_data.iloc[:2, :2]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 59,
   "id": "b7b91354-56af-4970-b9eb-d7226b01eed8",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "year  visit\n",
       "2013  1        49.0\n",
       "      2        43.0\n",
       "2014  1        22.0\n",
       "      2        40.0\n",
       "Name: (Bob, HR), dtype: float64"
      ]
     },
     "execution_count": 59,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "health_data.loc[:, ('Bob', 'HR')]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 62,
   "id": "da061035-ee51-4c68-a801-c32ca6d40d8b",
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
       "    .dataframe thead tr th {\n",
       "        text-align: left;\n",
       "    }\n",
       "\n",
       "    .dataframe thead tr:last-of-type th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>subject</th>\n",
       "      <th>Bob</th>\n",
       "      <th>Guido</th>\n",
       "      <th>Sue</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>HR</th>\n",
       "      <th>HR</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th>visit</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>2013</th>\n",
       "      <th>1</th>\n",
       "      <td>49.0</td>\n",
       "      <td>37.0</td>\n",
       "      <td>33.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2014</th>\n",
       "      <th>1</th>\n",
       "      <td>22.0</td>\n",
       "      <td>46.0</td>\n",
       "      <td>35.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "subject      Bob Guido   Sue\n",
       "type          HR    HR    HR\n",
       "year visit                  \n",
       "2013 1      49.0  37.0  33.0\n",
       "2014 1      22.0  46.0  35.0"
      ]
     },
     "execution_count": 62,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "idx = pd.IndexSlice\n",
    "health_data.loc[idx[:, 1], idx[:, 'HR']]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 63,
   "id": "6186ea7f-0b22-494e-a5bc-f897223b289a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "char  int\n",
       "a     1      0.617857\n",
       "      2      0.704381\n",
       "c     1      0.356883\n",
       "      2      0.141801\n",
       "b     1      0.622593\n",
       "      2      0.786514\n",
       "dtype: float64"
      ]
     },
     "execution_count": 63,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "index = pd.MultiIndex.from_product([['a', 'c', 'b'], [1, 2]])\n",
    "data = pd.Series(np.random.rand(6), index=index)\n",
    "data.index.names = ['char', 'int']\n",
    "data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 64,
   "id": "ebd32db3-50dc-48e9-9715-6b4c36603daa",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "<class 'pandas.errors.UnsortedIndexError'>\n",
      "'Key length (1) was greater than MultiIndex lexsort depth (0)'\n"
     ]
    }
   ],
   "source": [
    "try:\n",
    "    data['a':'b']\n",
    "except KeyError as e:\n",
    "    print(type(e))\n",
    "    print(e)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 65,
   "id": "2591b9e1-398e-4ad8-b6c6-f4d2fc9998e3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "char  int\n",
       "a     1      0.617857\n",
       "      2      0.704381\n",
       "b     1      0.622593\n",
       "      2      0.786514\n",
       "c     1      0.356883\n",
       "      2      0.141801\n",
       "dtype: float64"
      ]
     },
     "execution_count": 65,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data = data.sort_index()\n",
    "data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "id": "a476b952-f359-4e97-9161-3a663d50d376",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "char  int\n",
       "a     1      0.617857\n",
       "      2      0.704381\n",
       "b     1      0.622593\n",
       "      2      0.786514\n",
       "dtype: float64"
      ]
     },
     "execution_count": 66,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data['a':'b']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "id": "2ca63cfa-b281-436d-b2d2-5e1e3b649655",
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
       "      <th>state</th>\n",
       "      <th>California</th>\n",
       "      <th>New York</th>\n",
       "      <th>Texas</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>2000</th>\n",
       "      <td>33871648</td>\n",
       "      <td>18976457</td>\n",
       "      <td>20851820</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2010</th>\n",
       "      <td>37253956</td>\n",
       "      <td>19378102</td>\n",
       "      <td>25145561</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "state  California  New York     Texas\n",
       "year                                 \n",
       "2000     33871648  18976457  20851820\n",
       "2010     37253956  19378102  25145561"
      ]
     },
     "execution_count": 67,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop.unstack(level=0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "id": "8057f14d-7163-4e8b-8adb-020a9837577a",
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
       "      <th>year</th>\n",
       "      <th>2000</th>\n",
       "      <th>2010</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>state</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>California</th>\n",
       "      <td>33871648</td>\n",
       "      <td>37253956</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>New York</th>\n",
       "      <td>18976457</td>\n",
       "      <td>19378102</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Texas</th>\n",
       "      <td>20851820</td>\n",
       "      <td>25145561</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "year            2000      2010\n",
       "state                         \n",
       "California  33871648  37253956\n",
       "New York    18976457  19378102\n",
       "Texas       20851820  25145561"
      ]
     },
     "execution_count": 68,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop.unstack(level=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 69,
   "id": "496a65b2-aa0a-4705-95ba-8b3e9cb7e673",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "state       year\n",
       "California  2000    33871648\n",
       "            2010    37253956\n",
       "New York    2000    18976457\n",
       "            2010    19378102\n",
       "Texas       2000    20851820\n",
       "            2010    25145561\n",
       "dtype: int64"
      ]
     },
     "execution_count": 69,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop.unstack().stack()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 70,
   "id": "0ba9ee6c-f39c-4f7a-b748-9c30b64d52e6",
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
       "      <th>state</th>\n",
       "      <th>year</th>\n",
       "      <th>population</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>California</td>\n",
       "      <td>2000</td>\n",
       "      <td>33871648</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>California</td>\n",
       "      <td>2010</td>\n",
       "      <td>37253956</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>New York</td>\n",
       "      <td>2000</td>\n",
       "      <td>18976457</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>New York</td>\n",
       "      <td>2010</td>\n",
       "      <td>19378102</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>Texas</td>\n",
       "      <td>2000</td>\n",
       "      <td>20851820</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>Texas</td>\n",
       "      <td>2010</td>\n",
       "      <td>25145561</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "        state  year  population\n",
       "0  California  2000    33871648\n",
       "1  California  2010    37253956\n",
       "2    New York  2000    18976457\n",
       "3    New York  2010    19378102\n",
       "4       Texas  2000    20851820\n",
       "5       Texas  2010    25145561"
      ]
     },
     "execution_count": 70,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop_flat = pop.reset_index(name='population')\n",
    "pop_flat"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 71,
   "id": "4e67b8ea-8331-4ec5-96fd-03101e4a2abb",
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
       "      <th></th>\n",
       "      <th>population</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>state</th>\n",
       "      <th>year</th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">California</th>\n",
       "      <th>2000</th>\n",
       "      <td>33871648</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2010</th>\n",
       "      <td>37253956</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">New York</th>\n",
       "      <th>2000</th>\n",
       "      <td>18976457</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2010</th>\n",
       "      <td>19378102</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">Texas</th>\n",
       "      <th>2000</th>\n",
       "      <td>20851820</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2010</th>\n",
       "      <td>25145561</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                 population\n",
       "state      year            \n",
       "California 2000    33871648\n",
       "           2010    37253956\n",
       "New York   2000    18976457\n",
       "           2010    19378102\n",
       "Texas      2000    20851820\n",
       "           2010    25145561"
      ]
     },
     "execution_count": 71,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pop_flat.set_index(['state', 'year'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "id": "76f64c1e-51ab-4675-af1c-e77ddcb160fb",
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
       "    .dataframe thead tr th {\n",
       "        text-align: left;\n",
       "    }\n",
       "\n",
       "    .dataframe thead tr:last-of-type th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>subject</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Bob</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Guido</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Sue</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th>visit</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2013</th>\n",
       "      <th>1</th>\n",
       "      <td>49.0</td>\n",
       "      <td>38.5</td>\n",
       "      <td>37.0</td>\n",
       "      <td>38.2</td>\n",
       "      <td>33.0</td>\n",
       "      <td>38.3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>43.0</td>\n",
       "      <td>38.6</td>\n",
       "      <td>23.0</td>\n",
       "      <td>37.5</td>\n",
       "      <td>42.0</td>\n",
       "      <td>35.2</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th rowspan=\"2\" valign=\"top\">2014</th>\n",
       "      <th>1</th>\n",
       "      <td>22.0</td>\n",
       "      <td>37.3</td>\n",
       "      <td>46.0</td>\n",
       "      <td>36.5</td>\n",
       "      <td>35.0</td>\n",
       "      <td>37.3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>40.0</td>\n",
       "      <td>36.9</td>\n",
       "      <td>58.0</td>\n",
       "      <td>37.1</td>\n",
       "      <td>48.0</td>\n",
       "      <td>35.8</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "subject      Bob       Guido         Sue      \n",
       "type          HR  Temp    HR  Temp    HR  Temp\n",
       "year visit                                    \n",
       "2013 1      49.0  38.5  37.0  38.2  33.0  38.3\n",
       "     2      43.0  38.6  23.0  37.5  42.0  35.2\n",
       "2014 1      22.0  37.3  46.0  36.5  35.0  37.3\n",
       "     2      40.0  36.9  58.0  37.1  48.0  35.8"
      ]
     },
     "execution_count": 72,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "health_data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 76,
   "id": "478121ee-78c0-4f0f-b226-d3c7d47e6eb8",
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
       "    .dataframe thead tr th {\n",
       "        text-align: left;\n",
       "    }\n",
       "\n",
       "    .dataframe thead tr:last-of-type th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr>\n",
       "      <th>subject</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Bob</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Guido</th>\n",
       "      <th colspan=\"2\" halign=\"left\">Sue</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>2013</th>\n",
       "      <td>46.0</td>\n",
       "      <td>38.55</td>\n",
       "      <td>30.0</td>\n",
       "      <td>37.85</td>\n",
       "      <td>37.5</td>\n",
       "      <td>36.75</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2014</th>\n",
       "      <td>31.0</td>\n",
       "      <td>37.10</td>\n",
       "      <td>52.0</td>\n",
       "      <td>36.80</td>\n",
       "      <td>41.5</td>\n",
       "      <td>36.55</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "subject   Bob        Guido          Sue       \n",
       "type       HR   Temp    HR   Temp    HR   Temp\n",
       "year                                          \n",
       "2013     46.0  38.55  30.0  37.85  37.5  36.75\n",
       "2014     31.0  37.10  52.0  36.80  41.5  36.55"
      ]
     },
     "execution_count": 76,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data_mean = health_data.groupby(level='year').mean()\n",
    "data_mean\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 78,
   "id": "02eea5df-9a32-451a-9e77-230df16e8dc4",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_18940\\900051928.py:1: FutureWarning: DataFrame.groupby with axis=1 is deprecated. Do `frame.T.groupby(...)` without axis instead.\n",
      "  data_mean.groupby(axis=1, level='type').mean()\n"
     ]
    },
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
       "      <th>type</th>\n",
       "      <th>HR</th>\n",
       "      <th>Temp</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>year</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>2013</th>\n",
       "      <td>37.833333</td>\n",
       "      <td>37.716667</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2014</th>\n",
       "      <td>41.500000</td>\n",
       "      <td>36.816667</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "type         HR       Temp\n",
       "year                      \n",
       "2013  37.833333  37.716667\n",
       "2014  41.500000  36.816667"
      ]
     },
     "execution_count": 78,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data_mean.groupby(axis=1, level='type').mean()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5e820d27-723f-4254-adfb-a55903baa80f",
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
   "version": "3.12.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
