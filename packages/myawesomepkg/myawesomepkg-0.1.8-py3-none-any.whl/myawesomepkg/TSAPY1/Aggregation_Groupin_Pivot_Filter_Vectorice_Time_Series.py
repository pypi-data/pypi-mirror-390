{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "4f69a04d-f81c-4de7-9fcd-9e8e53dde5d2",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(1035, 6)"
      ]
     },
     "execution_count": 6,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " # Aggregation and Grouping\n",
    " import seaborn as sns\n",
    " import numpy as np\n",
    " import pandas as pd\n",
    "\n",
    " planets = sns.load_dataset('planets')\n",
    " planets.shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "d0a85e69-4dee-4a89-af0b-0b1619214246",
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
       "      <th>method</th>\n",
       "      <th>number</th>\n",
       "      <th>orbital_period</th>\n",
       "      <th>mass</th>\n",
       "      <th>distance</th>\n",
       "      <th>year</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Radial Velocity</td>\n",
       "      <td>1</td>\n",
       "      <td>269.300</td>\n",
       "      <td>7.10</td>\n",
       "      <td>77.40</td>\n",
       "      <td>2006</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Radial Velocity</td>\n",
       "      <td>1</td>\n",
       "      <td>874.774</td>\n",
       "      <td>2.21</td>\n",
       "      <td>56.95</td>\n",
       "      <td>2008</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Radial Velocity</td>\n",
       "      <td>1</td>\n",
       "      <td>763.000</td>\n",
       "      <td>2.60</td>\n",
       "      <td>19.84</td>\n",
       "      <td>2011</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Radial Velocity</td>\n",
       "      <td>1</td>\n",
       "      <td>326.030</td>\n",
       "      <td>19.40</td>\n",
       "      <td>110.62</td>\n",
       "      <td>2007</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>Radial Velocity</td>\n",
       "      <td>1</td>\n",
       "      <td>516.220</td>\n",
       "      <td>10.50</td>\n",
       "      <td>119.47</td>\n",
       "      <td>2009</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "            method  number  orbital_period   mass  distance  year\n",
       "0  Radial Velocity       1         269.300   7.10     77.40  2006\n",
       "1  Radial Velocity       1         874.774   2.21     56.95  2008\n",
       "2  Radial Velocity       1         763.000   2.60     19.84  2011\n",
       "3  Radial Velocity       1         326.030  19.40    110.62  2007\n",
       "4  Radial Velocity       1         516.220  10.50    119.47  2009"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "planets.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "a3af591e-4d36-421f-9193-a531fbf71daf",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    0.374540\n",
       "1    0.950714\n",
       "2    0.731994\n",
       "3    0.598658\n",
       "4    0.156019\n",
       "dtype: float64"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "rng = np.random.RandomState(42)\n",
    "ser = pd.Series(rng.rand(5))\n",
    "ser"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "e1551693-5459-4fda-ad83-6bf8983da04e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "np.float64(2.811925491708157)"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ser.sum()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "4229b069-a49f-4a35-a2a4-4c72665c3f15",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "np.float64(0.5623850983416314)"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ser.mean()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "09eb4bfb-5496-4e30-9c93-c50663b5466d",
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
       "      <th>A</th>\n",
       "      <th>B</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>0.183405</td>\n",
       "      <td>0.611853</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>0.304242</td>\n",
       "      <td>0.139494</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>0.524756</td>\n",
       "      <td>0.292145</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>0.431945</td>\n",
       "      <td>0.366362</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>0.291229</td>\n",
       "      <td>0.456070</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "          A         B\n",
       "0  0.183405  0.611853\n",
       "1  0.304242  0.139494\n",
       "2  0.524756  0.292145\n",
       "3  0.431945  0.366362\n",
       "4  0.291229  0.456070"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df = pd.DataFrame({'A': rng.rand(5),\n",
    " 'B': rng.rand(5)})\n",
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "dd941315-2e2b-42a4-80a9-a50dc81a291d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "A    0.347115\n",
       "B    0.373185\n",
       "dtype: float64"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.mean()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "b1c5221c-fd2f-44aa-a2a7-64cf11940039",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    0.397629\n",
       "1    0.221868\n",
       "2    0.408451\n",
       "3    0.399153\n",
       "4    0.373650\n",
       "dtype: float64"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.mean(axis='columns')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "3c3c9815-5ff7-4522-9b78-f79b7d2749c2",
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
       "      <th>number</th>\n",
       "      <th>orbital_period</th>\n",
       "      <th>mass</th>\n",
       "      <th>distance</th>\n",
       "      <th>year</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>count</th>\n",
       "      <td>498.00000</td>\n",
       "      <td>498.000000</td>\n",
       "      <td>498.000000</td>\n",
       "      <td>498.000000</td>\n",
       "      <td>498.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>mean</th>\n",
       "      <td>1.73494</td>\n",
       "      <td>835.778671</td>\n",
       "      <td>2.509320</td>\n",
       "      <td>52.068213</td>\n",
       "      <td>2007.377510</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>std</th>\n",
       "      <td>1.17572</td>\n",
       "      <td>1469.128259</td>\n",
       "      <td>3.636274</td>\n",
       "      <td>46.596041</td>\n",
       "      <td>4.167284</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>min</th>\n",
       "      <td>1.00000</td>\n",
       "      <td>1.328300</td>\n",
       "      <td>0.003600</td>\n",
       "      <td>1.350000</td>\n",
       "      <td>1989.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>25%</th>\n",
       "      <td>1.00000</td>\n",
       "      <td>38.272250</td>\n",
       "      <td>0.212500</td>\n",
       "      <td>24.497500</td>\n",
       "      <td>2005.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>50%</th>\n",
       "      <td>1.00000</td>\n",
       "      <td>357.000000</td>\n",
       "      <td>1.245000</td>\n",
       "      <td>39.940000</td>\n",
       "      <td>2009.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>75%</th>\n",
       "      <td>2.00000</td>\n",
       "      <td>999.600000</td>\n",
       "      <td>2.867500</td>\n",
       "      <td>59.332500</td>\n",
       "      <td>2011.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>max</th>\n",
       "      <td>6.00000</td>\n",
       "      <td>17337.500000</td>\n",
       "      <td>25.000000</td>\n",
       "      <td>354.000000</td>\n",
       "      <td>2014.000000</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "          number  orbital_period        mass    distance         year\n",
       "count  498.00000      498.000000  498.000000  498.000000   498.000000\n",
       "mean     1.73494      835.778671    2.509320   52.068213  2007.377510\n",
       "std      1.17572     1469.128259    3.636274   46.596041     4.167284\n",
       "min      1.00000        1.328300    0.003600    1.350000  1989.000000\n",
       "25%      1.00000       38.272250    0.212500   24.497500  2005.000000\n",
       "50%      1.00000      357.000000    1.245000   39.940000  2009.000000\n",
       "75%      2.00000      999.600000    2.867500   59.332500  2011.000000\n",
       "max      6.00000    17337.500000   25.000000  354.000000  2014.000000"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "planets.dropna().describe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "443f472b-83a4-4468-a104-5fc39c327453",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "          A         B\n",
      "0  0.183405  0.611853\n",
      "1  0.304242  0.139494\n",
      "2  0.524756  0.292145\n",
      "3  0.431945  0.366362\n",
      "4  0.291229  0.456070\n"
     ]
    },
    {
     "ename": "KeyError",
     "evalue": "'key'",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mKeyError\u001b[0m                                  Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[18], line 3\u001b[0m\n\u001b[0;32m      1\u001b[0m \u001b[38;5;28;01mdef\u001b[39;00m \u001b[38;5;21mfilter_func\u001b[39m(x):\n\u001b[0;32m      2\u001b[0m    \u001b[38;5;28;01mreturn\u001b[39;00m x[\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mdata2\u001b[39m\u001b[38;5;124m'\u001b[39m]\u001b[38;5;241m.\u001b[39mstd() \u001b[38;5;241m>\u001b[39m \u001b[38;5;241m4\u001b[39m\n\u001b[1;32m----> 3\u001b[0m \u001b[38;5;28mprint\u001b[39m(df); \u001b[38;5;28mprint\u001b[39m(df\u001b[38;5;241m.\u001b[39mgroupby(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mkey\u001b[39m\u001b[38;5;124m'\u001b[39m)\u001b[38;5;241m.\u001b[39mstd());\n\u001b[0;32m      4\u001b[0m \u001b[38;5;28mprint\u001b[39m(df\u001b[38;5;241m.\u001b[39mgroupby(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mkey\u001b[39m\u001b[38;5;124m'\u001b[39m)\u001b[38;5;241m.\u001b[39mfilter(filter_func))\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\frame.py:9183\u001b[0m, in \u001b[0;36mDataFrame.groupby\u001b[1;34m(self, by, axis, level, as_index, sort, group_keys, observed, dropna)\u001b[0m\n\u001b[0;32m   9180\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m level \u001b[38;5;129;01mis\u001b[39;00m \u001b[38;5;28;01mNone\u001b[39;00m \u001b[38;5;129;01mand\u001b[39;00m by \u001b[38;5;129;01mis\u001b[39;00m \u001b[38;5;28;01mNone\u001b[39;00m:\n\u001b[0;32m   9181\u001b[0m     \u001b[38;5;28;01mraise\u001b[39;00m \u001b[38;5;167;01mTypeError\u001b[39;00m(\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mYou have to supply one of \u001b[39m\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mby\u001b[39m\u001b[38;5;124m'\u001b[39m\u001b[38;5;124m and \u001b[39m\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mlevel\u001b[39m\u001b[38;5;124m'\u001b[39m\u001b[38;5;124m\"\u001b[39m)\n\u001b[1;32m-> 9183\u001b[0m \u001b[38;5;28;01mreturn\u001b[39;00m \u001b[43mDataFrameGroupBy\u001b[49m\u001b[43m(\u001b[49m\n\u001b[0;32m   9184\u001b[0m \u001b[43m    \u001b[49m\u001b[43mobj\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[38;5;28;43mself\u001b[39;49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9185\u001b[0m \u001b[43m    \u001b[49m\u001b[43mkeys\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43mby\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9186\u001b[0m \u001b[43m    \u001b[49m\u001b[43maxis\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43maxis\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9187\u001b[0m \u001b[43m    \u001b[49m\u001b[43mlevel\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43mlevel\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9188\u001b[0m \u001b[43m    \u001b[49m\u001b[43mas_index\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43mas_index\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9189\u001b[0m \u001b[43m    \u001b[49m\u001b[43msort\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43msort\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9190\u001b[0m \u001b[43m    \u001b[49m\u001b[43mgroup_keys\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43mgroup_keys\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9191\u001b[0m \u001b[43m    \u001b[49m\u001b[43mobserved\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43mobserved\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9192\u001b[0m \u001b[43m    \u001b[49m\u001b[43mdropna\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43mdropna\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   9193\u001b[0m \u001b[43m\u001b[49m\u001b[43m)\u001b[49m\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\groupby\\groupby.py:1329\u001b[0m, in \u001b[0;36mGroupBy.__init__\u001b[1;34m(self, obj, keys, axis, level, grouper, exclusions, selection, as_index, sort, group_keys, observed, dropna)\u001b[0m\n\u001b[0;32m   1326\u001b[0m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39mdropna \u001b[38;5;241m=\u001b[39m dropna\n\u001b[0;32m   1328\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m grouper \u001b[38;5;129;01mis\u001b[39;00m \u001b[38;5;28;01mNone\u001b[39;00m:\n\u001b[1;32m-> 1329\u001b[0m     grouper, exclusions, obj \u001b[38;5;241m=\u001b[39m \u001b[43mget_grouper\u001b[49m\u001b[43m(\u001b[49m\n\u001b[0;32m   1330\u001b[0m \u001b[43m        \u001b[49m\u001b[43mobj\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   1331\u001b[0m \u001b[43m        \u001b[49m\u001b[43mkeys\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   1332\u001b[0m \u001b[43m        \u001b[49m\u001b[43maxis\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43maxis\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   1333\u001b[0m \u001b[43m        \u001b[49m\u001b[43mlevel\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43mlevel\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   1334\u001b[0m \u001b[43m        \u001b[49m\u001b[43msort\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43msort\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   1335\u001b[0m \u001b[43m        \u001b[49m\u001b[43mobserved\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[38;5;28;43;01mFalse\u001b[39;49;00m\u001b[43m \u001b[49m\u001b[38;5;28;43;01mif\u001b[39;49;00m\u001b[43m \u001b[49m\u001b[43mobserved\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;129;43;01mis\u001b[39;49;00m\u001b[43m \u001b[49m\u001b[43mlib\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mno_default\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;28;43;01melse\u001b[39;49;00m\u001b[43m \u001b[49m\u001b[43mobserved\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   1336\u001b[0m \u001b[43m        \u001b[49m\u001b[43mdropna\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[38;5;28;43mself\u001b[39;49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mdropna\u001b[49m\u001b[43m,\u001b[49m\n\u001b[0;32m   1337\u001b[0m \u001b[43m    \u001b[49m\u001b[43m)\u001b[49m\n\u001b[0;32m   1339\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m observed \u001b[38;5;129;01mis\u001b[39;00m lib\u001b[38;5;241m.\u001b[39mno_default:\n\u001b[0;32m   1340\u001b[0m     \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;28many\u001b[39m(ping\u001b[38;5;241m.\u001b[39m_passed_categorical \u001b[38;5;28;01mfor\u001b[39;00m ping \u001b[38;5;129;01min\u001b[39;00m grouper\u001b[38;5;241m.\u001b[39mgroupings):\n",
      "File \u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\groupby\\grouper.py:1043\u001b[0m, in \u001b[0;36mget_grouper\u001b[1;34m(obj, key, axis, level, sort, observed, validate, dropna)\u001b[0m\n\u001b[0;32m   1041\u001b[0m         in_axis, level, gpr \u001b[38;5;241m=\u001b[39m \u001b[38;5;28;01mFalse\u001b[39;00m, gpr, \u001b[38;5;28;01mNone\u001b[39;00m\n\u001b[0;32m   1042\u001b[0m     \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[1;32m-> 1043\u001b[0m         \u001b[38;5;28;01mraise\u001b[39;00m \u001b[38;5;167;01mKeyError\u001b[39;00m(gpr)\n\u001b[0;32m   1044\u001b[0m \u001b[38;5;28;01melif\u001b[39;00m \u001b[38;5;28misinstance\u001b[39m(gpr, Grouper) \u001b[38;5;129;01mand\u001b[39;00m gpr\u001b[38;5;241m.\u001b[39mkey \u001b[38;5;129;01mis\u001b[39;00m \u001b[38;5;129;01mnot\u001b[39;00m \u001b[38;5;28;01mNone\u001b[39;00m:\n\u001b[0;32m   1045\u001b[0m     \u001b[38;5;66;03m# Add key to exclusions\u001b[39;00m\n\u001b[0;32m   1046\u001b[0m     exclusions\u001b[38;5;241m.\u001b[39madd(gpr\u001b[38;5;241m.\u001b[39mkey)\n",
      "\u001b[1;31mKeyError\u001b[0m: 'key'"
     ]
    }
   ],
   "source": [
    " def filter_func(x):\n",
    "    return x['data2'].std() > 4\n",
    " print(df); print(df.groupby('key').std());\n",
    " print(df.groupby('key').filter(filter_func))\n",
    " "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "40071505-de3c-4940-89ea-d38b0f1212b8",
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
       "      <th>key</th>\n",
       "      <th>data1</th>\n",
       "      <th>data2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>A</td>\n",
       "      <td>0</td>\n",
       "      <td>5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>B</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>C</td>\n",
       "      <td>2</td>\n",
       "      <td>3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>A</td>\n",
       "      <td>3</td>\n",
       "      <td>3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>B</td>\n",
       "      <td>4</td>\n",
       "      <td>7</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>C</td>\n",
       "      <td>5</td>\n",
       "      <td>9</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  key  data1  data2\n",
       "0   A      0      5\n",
       "1   B      1      0\n",
       "2   C      2      3\n",
       "3   A      3      3\n",
       "4   B      4      7\n",
       "5   C      5      9"
      ]
     },
     "execution_count": 22,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Aggregate, ilter, transform, apply\n",
    "rng = np.random.RandomState(0)\n",
    "df = pd.DataFrame({'key': ['A', 'B', 'C', 'A', 'B', 'C'],\n",
    " 'data1': range(6),\n",
    " 'data2': rng.randint(0, 10, 6)},\n",
    " columns = ['key', 'data1', 'data2'])\n",
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "2c3e28cc-a33e-4567-8b3c-84f243692d1c",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_1940\\968873422.py:1: FutureWarning: The provided callable <function median at 0x00000235EACE3060> is currently using SeriesGroupBy.median. In a future version of pandas, the provided callable will be used directly. To keep current behavior pass the string \"median\" instead.\n",
      "  df.groupby('key').aggregate(['min', np.median, max])\n",
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_1940\\968873422.py:1: FutureWarning: The provided callable <built-in function max> is currently using SeriesGroupBy.max. In a future version of pandas, the provided callable will be used directly. To keep current behavior pass the string \"max\" instead.\n",
      "  df.groupby('key').aggregate(['min', np.median, max])\n"
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
       "      <th colspan=\"3\" halign=\"left\">data1</th>\n",
       "      <th colspan=\"3\" halign=\"left\">data2</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th></th>\n",
       "      <th>min</th>\n",
       "      <th>median</th>\n",
       "      <th>max</th>\n",
       "      <th>min</th>\n",
       "      <th>median</th>\n",
       "      <th>max</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>key</th>\n",
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
       "      <th>A</th>\n",
       "      <td>0</td>\n",
       "      <td>1.5</td>\n",
       "      <td>3</td>\n",
       "      <td>3</td>\n",
       "      <td>4.0</td>\n",
       "      <td>5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>B</th>\n",
       "      <td>1</td>\n",
       "      <td>2.5</td>\n",
       "      <td>4</td>\n",
       "      <td>0</td>\n",
       "      <td>3.5</td>\n",
       "      <td>7</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>C</th>\n",
       "      <td>2</td>\n",
       "      <td>3.5</td>\n",
       "      <td>5</td>\n",
       "      <td>3</td>\n",
       "      <td>6.0</td>\n",
       "      <td>9</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "    data1            data2           \n",
       "      min median max   min median max\n",
       "key                                  \n",
       "A       0    1.5   3     3    4.0   5\n",
       "B       1    2.5   4     0    3.5   7\n",
       "C       2    3.5   5     3    6.0   9"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.groupby('key').aggregate(['min', np.median, max])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "c05f9979-f316-4c52-8398-7b4db4623523",
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
       "      <th>data1</th>\n",
       "      <th>data2</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>key</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>A</th>\n",
       "      <td>0</td>\n",
       "      <td>5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>B</th>\n",
       "      <td>1</td>\n",
       "      <td>7</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>C</th>\n",
       "      <td>2</td>\n",
       "      <td>9</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     data1  data2\n",
       "key              \n",
       "A        0      5\n",
       "B        1      7\n",
       "C        2      9"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " df.groupby('key').aggregate({'data1': 'min',\n",
    "                                     'data2': 'max'})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "c065e650-3fe4-46a3-b1c0-a12c2b854bf3",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  key  data1  data2\n",
      "0   A      0      5\n",
      "1   B      1      0\n",
      "2   C      2      3\n",
      "3   A      3      3\n",
      "4   B      4      7\n",
      "5   C      5      9\n",
      "       data1     data2\n",
      "key                   \n",
      "A    2.12132  1.414214\n",
      "B    2.12132  4.949747\n",
      "C    2.12132  4.242641\n",
      "  key  data1  data2\n",
      "1   B      1      0\n",
      "2   C      2      3\n",
      "4   B      4      7\n",
      "5   C      5      9\n"
     ]
    }
   ],
   "source": [
    "# Filtering.   \n",
    "def filter_func(x):\n",
    "    return x['data2'].std() > 4\n",
    "print(df); print(df.groupby('key').std());\n",
    "print(df.groupby('key').filter(filter_func))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "a0f958e6-d237-45df-b85b-483bcb13dfee",
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
       "      <th>key</th>\n",
       "      <th>data1</th>\n",
       "      <th>data2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>B</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>C</td>\n",
       "      <td>2</td>\n",
       "      <td>3</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>B</td>\n",
       "      <td>4</td>\n",
       "      <td>7</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>C</td>\n",
       "      <td>5</td>\n",
       "      <td>9</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  key  data1  data2\n",
       "1   B      1      0\n",
       "2   C      2      3\n",
       "4   B      4      7\n",
       "5   C      5      9"
      ]
     },
     "execution_count": 28,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df.groupby('key').filter(filter_func)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "6357cbab-c99d-470c-83b3-22a8edcbd7ac",
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
       "      <th>data1</th>\n",
       "      <th>data2</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>-1.5</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>-1.5</td>\n",
       "      <td>-3.5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>-1.5</td>\n",
       "      <td>-3.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>1.5</td>\n",
       "      <td>-1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>1.5</td>\n",
       "      <td>3.5</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>1.5</td>\n",
       "      <td>3.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   data1  data2\n",
       "0   -1.5    1.0\n",
       "1   -1.5   -3.5\n",
       "2   -1.5   -3.0\n",
       "3    1.5   -1.0\n",
       "4    1.5    3.5\n",
       "5    1.5    3.0"
      ]
     },
     "execution_count": 29,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " df.groupby('key').transform(lambda x: x - x.mean())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "eace356a-087d-4376-84ad-70096afc5f8a",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  key  data1  data2\n",
      "0   A      0      5\n",
      "1   B      1      0\n",
      "2   C      2      3\n",
      "3   A      3      3\n",
      "4   B      4      7\n",
      "5   C      5      9\n",
      "      key     data1  data2\n",
      "key                       \n",
      "A   0   A  0.000000      5\n",
      "    3   A  0.375000      3\n",
      "B   1   B  0.142857      0\n",
      "    4   B  0.571429      7\n",
      "C   2   C  0.166667      3\n",
      "    5   C  0.416667      9\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_1940\\3133374050.py:6: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.\n",
      "  print(df); print(df.groupby('key').apply(norm_by_data2))\n"
     ]
    }
   ],
   "source": [
    " # The apply() method.\n",
    " def norm_by_data2(x):\n",
    "            # x is a DataFrame of group values\n",
    "            x['data1'] /= x['data2'].sum()\n",
    "            return x\n",
    " print(df); print(df.groupby('key').apply(norm_by_data2))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "ba028303-402d-4141-b284-e15df4855ff3",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  key  data1  data2\n",
      "0   A      0      5\n",
      "1   B      1      0\n",
      "2   C      2      3\n",
      "3   A      3      3\n",
      "4   B      4      7\n",
      "5   C      5      9\n",
      "   key  data1  data2\n",
      "0  ACC      7     17\n",
      "1   BA      4      3\n",
      "2    B      4      7\n"
     ]
    }
   ],
   "source": [
    "#Specifying the split key\n",
    "L = [0, 1, 0, 1, 2, 0]\n",
    "print(df); print(df.groupby(L).sum())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "id": "cd2e7ff6-2aaa-4fe4-9efd-d852e2de7cfd",
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
       "      <th>decade</th>\n",
       "      <th>1980s</th>\n",
       "      <th>1990s</th>\n",
       "      <th>2000s</th>\n",
       "      <th>2010s</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>method</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>Astrometry</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>2.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Eclipse Timing Variations</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>5.0</td>\n",
       "      <td>10.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Imaging</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>29.0</td>\n",
       "      <td>21.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Microlensing</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>12.0</td>\n",
       "      <td>15.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Orbital Brightness Modulation</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>5.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Pulsar Timing</th>\n",
       "      <td>0.0</td>\n",
       "      <td>9.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Pulsation Timing Variations</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>0.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Radial Velocity</th>\n",
       "      <td>1.0</td>\n",
       "      <td>52.0</td>\n",
       "      <td>475.0</td>\n",
       "      <td>424.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Transit</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>64.0</td>\n",
       "      <td>712.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Transit Timing Variations</th>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>9.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "decade                         1980s  1990s  2000s  2010s\n",
       "method                                                   \n",
       "Astrometry                       0.0    0.0    0.0    2.0\n",
       "Eclipse Timing Variations        0.0    0.0    5.0   10.0\n",
       "Imaging                          0.0    0.0   29.0   21.0\n",
       "Microlensing                     0.0    0.0   12.0   15.0\n",
       "Orbital Brightness Modulation    0.0    0.0    0.0    5.0\n",
       "Pulsar Timing                    0.0    9.0    1.0    1.0\n",
       "Pulsation Timing Variations      0.0    0.0    1.0    0.0\n",
       "Radial Velocity                  1.0   52.0  475.0  424.0\n",
       "Transit                          0.0    0.0   64.0  712.0\n",
       "Transit Timing Variations        0.0    0.0    0.0    9.0"
      ]
     },
     "execution_count": 33,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Grouping example\n",
    "decade = 10 * (planets['year'] // 10)\n",
    "decade = decade.astype(str) + 's'\n",
    "decade.name = 'decade'\n",
    "planets.groupby(['method', decade])['number'].sum().unstack().fillna(0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "68c8eaac-b321-4e5a-bfda-7366061c8ec3",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Pivot Tables\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import seaborn as sns\n",
    "titanic = sns.load_dataset('titanic')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "fe9c52f9-e461-483f-bfd1-36400787c720",
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
       "      <th>survived</th>\n",
       "      <th>pclass</th>\n",
       "      <th>sex</th>\n",
       "      <th>age</th>\n",
       "      <th>sibsp</th>\n",
       "      <th>parch</th>\n",
       "      <th>fare</th>\n",
       "      <th>embarked</th>\n",
       "      <th>class</th>\n",
       "      <th>who</th>\n",
       "      <th>adult_male</th>\n",
       "      <th>deck</th>\n",
       "      <th>embark_town</th>\n",
       "      <th>alive</th>\n",
       "      <th>alone</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>0</td>\n",
       "      <td>3</td>\n",
       "      <td>male</td>\n",
       "      <td>22.0</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>7.2500</td>\n",
       "      <td>S</td>\n",
       "      <td>Third</td>\n",
       "      <td>man</td>\n",
       "      <td>True</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Southampton</td>\n",
       "      <td>no</td>\n",
       "      <td>False</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>1</td>\n",
       "      <td>1</td>\n",
       "      <td>female</td>\n",
       "      <td>38.0</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>71.2833</td>\n",
       "      <td>C</td>\n",
       "      <td>First</td>\n",
       "      <td>woman</td>\n",
       "      <td>False</td>\n",
       "      <td>C</td>\n",
       "      <td>Cherbourg</td>\n",
       "      <td>yes</td>\n",
       "      <td>False</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>1</td>\n",
       "      <td>3</td>\n",
       "      <td>female</td>\n",
       "      <td>26.0</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>7.9250</td>\n",
       "      <td>S</td>\n",
       "      <td>Third</td>\n",
       "      <td>woman</td>\n",
       "      <td>False</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Southampton</td>\n",
       "      <td>yes</td>\n",
       "      <td>True</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>1</td>\n",
       "      <td>1</td>\n",
       "      <td>female</td>\n",
       "      <td>35.0</td>\n",
       "      <td>1</td>\n",
       "      <td>0</td>\n",
       "      <td>53.1000</td>\n",
       "      <td>S</td>\n",
       "      <td>First</td>\n",
       "      <td>woman</td>\n",
       "      <td>False</td>\n",
       "      <td>C</td>\n",
       "      <td>Southampton</td>\n",
       "      <td>yes</td>\n",
       "      <td>False</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>0</td>\n",
       "      <td>3</td>\n",
       "      <td>male</td>\n",
       "      <td>35.0</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>8.0500</td>\n",
       "      <td>S</td>\n",
       "      <td>Third</td>\n",
       "      <td>man</td>\n",
       "      <td>True</td>\n",
       "      <td>NaN</td>\n",
       "      <td>Southampton</td>\n",
       "      <td>no</td>\n",
       "      <td>True</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   survived  pclass     sex   age  sibsp  parch     fare embarked  class  \\\n",
       "0         0       3    male  22.0      1      0   7.2500        S  Third   \n",
       "1         1       1  female  38.0      1      0  71.2833        C  First   \n",
       "2         1       3  female  26.0      0      0   7.9250        S  Third   \n",
       "3         1       1  female  35.0      1      0  53.1000        S  First   \n",
       "4         0       3    male  35.0      0      0   8.0500        S  Third   \n",
       "\n",
       "     who  adult_male deck  embark_town alive  alone  \n",
       "0    man        True  NaN  Southampton    no  False  \n",
       "1  woman       False    C    Cherbourg   yes  False  \n",
       "2  woman       False  NaN  Southampton   yes   True  \n",
       "3  woman       False    C  Southampton   yes  False  \n",
       "4    man        True  NaN  Southampton    no   True  "
      ]
     },
     "execution_count": 35,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "titanic.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "id": "d9f3b1fc-5125-4058-8448-95f65d8decd6",
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
       "      <th>survived</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>sex</th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>female</th>\n",
       "      <td>0.742038</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>male</th>\n",
       "      <td>0.188908</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "        survived\n",
       "sex             \n",
       "female  0.742038\n",
       "male    0.188908"
      ]
     },
     "execution_count": 36,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "titanic.groupby('sex')[['survived']].mean()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "id": "96fc78d1-878a-4418-8b2c-1e6bae80c1f7",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\darsh\\AppData\\Local\\Temp\\ipykernel_1940\\2603839867.py:1: FutureWarning: The default of observed=False is deprecated and will be changed to True in a future version of pandas. Pass observed=False to retain current behavior or observed=True to adopt the future default and silence this warning.\n",
      "  titanic.groupby(['sex', 'class'])['survived'].aggregate('mean').unstack()\n"
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
       "      <th>class</th>\n",
       "      <th>First</th>\n",
       "      <th>Second</th>\n",
       "      <th>Third</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>sex</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>female</th>\n",
       "      <td>0.968085</td>\n",
       "      <td>0.921053</td>\n",
       "      <td>0.500000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>male</th>\n",
       "      <td>0.368852</td>\n",
       "      <td>0.157407</td>\n",
       "      <td>0.135447</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "class      First    Second     Third\n",
       "sex                                 \n",
       "female  0.968085  0.921053  0.500000\n",
       "male    0.368852  0.157407  0.135447"
      ]
     },
     "execution_count": 37,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "titanic.groupby(['sex', 'class'])['survived'].aggregate('mean').unstack()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "id": "28b5cad3-2411-4cd7-aa24-4a423e03b00b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 4,  6, 10, 14, 22, 26])"
      ]
     },
     "execution_count": 38,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Vectorized String Operation\n",
    "import numpy as np\n",
    "x = np.array([2, 3, 5, 7, 11, 13])\n",
    "x * 2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "id": "febdc11c-b284-4b43-a9c0-44001bc9dda3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "['Peter', 'Paul', 'Mary', 'Guido']"
      ]
     },
     "execution_count": 39,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data = ['peter', 'Paul', 'MARY', 'gUIDO']\n",
    "[s.capitalize() for s in data]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "id": "8d689e1a-ccdc-4916-b665-49cf7b21d02e",
   "metadata": {},
   "outputs": [
    {
     "ename": "AttributeError",
     "evalue": "'NoneType' object has no attribute 'capitalize'",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mAttributeError\u001b[0m                            Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[40], line 2\u001b[0m\n\u001b[0;32m      1\u001b[0m data \u001b[38;5;241m=\u001b[39m [\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mpeter\u001b[39m\u001b[38;5;124m'\u001b[39m, \u001b[38;5;124m'\u001b[39m\u001b[38;5;124mPaul\u001b[39m\u001b[38;5;124m'\u001b[39m, \u001b[38;5;28;01mNone\u001b[39;00m, \u001b[38;5;124m'\u001b[39m\u001b[38;5;124mMARY\u001b[39m\u001b[38;5;124m'\u001b[39m, \u001b[38;5;124m'\u001b[39m\u001b[38;5;124mgUIDO\u001b[39m\u001b[38;5;124m'\u001b[39m]\n\u001b[1;32m----> 2\u001b[0m [\u001b[43ms\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mcapitalize\u001b[49m() \u001b[38;5;28;01mfor\u001b[39;00m s \u001b[38;5;129;01min\u001b[39;00m data]\n",
      "\u001b[1;31mAttributeError\u001b[0m: 'NoneType' object has no attribute 'capitalize'"
     ]
    }
   ],
   "source": [
    "data = ['peter', 'Paul', None, 'MARY', 'gUIDO']\n",
    "[s.capitalize() for s in data]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "id": "8c2280ab-a3f9-424b-af89-97823534801e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    peter\n",
       "1     Paul\n",
       "2     None\n",
       "3     MARY\n",
       "4    gUIDO\n",
       "dtype: object"
      ]
     },
     "execution_count": 41,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import pandas as pd\n",
    "names = pd.Series(data)\n",
    "names"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "id": "c5271eae-68d8-4a39-8b78-e0509e0bdf6a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    Peter\n",
       "1     Paul\n",
       "2     None\n",
       "3     Mary\n",
       "4    Guido\n",
       "dtype: object"
      ]
     },
     "execution_count": 42,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " names.str.capitalize()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "id": "77c5a86f-9cc8-4c2d-9aa2-3901a484c83c",
   "metadata": {},
   "outputs": [],
   "source": [
    "monte = pd.Series(['Graham Chapman', 'John Cleese', 'Terry Gilliam',\n",
    " 'Eric Idle', 'Terry Jones', 'Michael Palin'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "id": "ce34f0ac-171b-4e08-a816-e39e348f2508",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    graham chapman\n",
       "1       john cleese\n",
       "2     terry gilliam\n",
       "3         eric idle\n",
       "4       terry jones\n",
       "5     michael palin\n",
       "dtype: object"
      ]
     },
     "execution_count": 45,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " monte.str.lower()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "id": "b5672c72-c2db-4425-8290-7944ec83c77c",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    14\n",
       "1    11\n",
       "2    13\n",
       "3     9\n",
       "4    11\n",
       "5    13\n",
       "dtype: int64"
      ]
     },
     "execution_count": 46,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " monte.str.len()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "id": "9c99eabc-b0f4-41d7-8de8-fd550a7e5448",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    [Graham, Chapman]\n",
       "1       [John, Cleese]\n",
       "2     [Terry, Gilliam]\n",
       "3         [Eric, Idle]\n",
       "4       [Terry, Jones]\n",
       "5     [Michael, Palin]\n",
       "dtype: object"
      ]
     },
     "execution_count": 47,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " monte.str.split()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "id": "e751ca4c-b6e3-4f50-a09e-10e1d1915eb4",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    Gra\n",
       "1    Joh\n",
       "2    Ter\n",
       "3    Eri\n",
       "4    Ter\n",
       "5    Mic\n",
       "dtype: object"
      ]
     },
     "execution_count": 48,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Vectorized item access and slicing\n",
    "monte.str[0:3]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "id": "6c7d9ce7-e394-4492-8ed5-8f7f3772bd0f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0    Chapman\n",
       "1     Cleese\n",
       "2    Gilliam\n",
       "3       Idle\n",
       "4      Jones\n",
       "5      Palin\n",
       "dtype: object"
      ]
     },
     "execution_count": 49,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "monte.str.split().str.get(-1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "id": "82f5029b-0cc0-4122-ab88-db298650a5c2",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "datetime.datetime(2015, 7, 4, 0, 0)"
      ]
     },
     "execution_count": 50,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " # Working with Time Serie\n",
    "from datetime import datetime\n",
    "datetime(year=2015, month=7, day=4)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "id": "60d56a09-8fd3-4168-89fb-04970425fee8",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "datetime.datetime(2015, 7, 4, 0, 0)"
      ]
     },
     "execution_count": 51,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " from dateutil import parser\n",
    " date = parser.parse(\"4th of July, 2015\")\n",
    " date"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "id": "5eae15bf-1a75-4565-b1d0-2b10cef44d3b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'Saturday'"
      ]
     },
     "execution_count": 52,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "date.strftime('%A')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "id": "d6cc3148-aeb7-447e-83b6-66037aad2b88",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array('2015-07-04', dtype='datetime64[D]')"
      ]
     },
     "execution_count": 54,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import numpy as np\n",
    "date = np.array('2015-07-04', dtype=np.datetime64)\n",
    "date"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 55,
   "id": "a504a4a8-5a0a-4c62-8c17-80d6124e657a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array(['2015-07-04', '2015-07-05', '2015-07-06', '2015-07-07',\n",
       "       '2015-07-08', '2015-07-09', '2015-07-10', '2015-07-11',\n",
       "       '2015-07-12', '2015-07-13', '2015-07-14', '2015-07-15'],\n",
       "      dtype='datetime64[D]')"
      ]
     },
     "execution_count": 55,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "date + np.arange(12)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 56,
   "id": "1d245780-95e0-480c-bfd3-9d1e2a3673c3",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "np.datetime64('2015-07-04')"
      ]
     },
     "execution_count": 56,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.datetime64('2015-07-04')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 57,
   "id": "3f94ee5e-43c8-4956-b004-3f9a850a9b19",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "np.datetime64('2015-07-04T12:00')"
      ]
     },
     "execution_count": 57,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.datetime64('2015-07-04 12:00')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 58,
   "id": "e8b9830a-584d-41c6-b387-d8244e3a012e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "np.datetime64('2015-07-04T12:59:59.500000000')"
      ]
     },
     "execution_count": 58,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " np.datetime64('2015-07-04 12:59:59.50', 'ns')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d63b7366-07ee-4baf-84a3-295458571d0f",
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
