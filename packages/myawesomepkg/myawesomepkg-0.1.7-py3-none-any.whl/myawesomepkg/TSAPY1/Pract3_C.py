{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "0a4a008c-1cc1-4881-afbd-d1e042af1116",
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
       "      <th>C</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>A0</td>\n",
       "      <td>B0</td>\n",
       "      <td>C0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>A1</td>\n",
       "      <td>B1</td>\n",
       "      <td>C1</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>A2</td>\n",
       "      <td>B2</td>\n",
       "      <td>C2</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "    A   B   C\n",
       "0  A0  B0  C0\n",
       "1  A1  B1  C1\n",
       "2  A2  B2  C2"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "def make_df(cols, ind):\n",
    "    data = {c: [str(c) + str(i) for i in ind]\n",
    "            for c in cols}\n",
    "    return pd.DataFrame(data, ind)\n",
    "\n",
    "make_df('ABC', range(3))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "01df54aa-d5a4-442d-bee8-f7ef978ff9aa",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([1, 2, 3, 4, 5, 6, 7, 8, 9])"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x = [1, 2, 3]\n",
    "y = [4, 5, 6]\n",
    "z = [7, 8, 9]\n",
    "np.concatenate([x, y, z])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "865938c6-668c-4015-b357-063e854bed46",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[1, 2, 1, 2],\n",
       "       [3, 4, 3, 4]])"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x = [[1, 2],\n",
    "[3, 4]]\n",
    "np.concatenate([x, x], axis=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "bee431f1-5b60-4972-aef6-ddcfad6dda02",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1    A\n",
       "2    B\n",
       "3    C\n",
       "4    D\n",
       "5    E\n",
       "6    F\n",
       "dtype: object"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ser1 = pd.Series(['A', 'B', 'C'], index=[1, 2, 3])\n",
    "ser2 = pd.Series(['D', 'E', 'F'], index=[4, 5, 6])\n",
    "pd.concat([ser1, ser2])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "309aa9ab-754e-430d-9070-35f9ba2275a1",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B\n",
      "1  A1  B1\n",
      "2  A2  B2\n",
      "    A   B\n",
      "3  A3  B3\n",
      "4  A4  B4\n",
      "    A   B\n",
      "1  A1  B1\n",
      "2  A2  B2\n",
      "3  A3  B3\n",
      "4  A4  B4\n"
     ]
    }
   ],
   "source": [
    "df1 = make_df('AB', [1, 2])\n",
    "df2 = make_df('AB', [3, 4])\n",
    "print(df1); print(df2); print(pd.concat([df1, df2]))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "78b97a80-adb7-4c50-8a9a-92df803d825d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B\n",
      "0  A0  B0\n",
      "1  A1  B1\n",
      "    C   D\n",
      "0  C0  D0\n",
      "1  C1  D1\n"
     ]
    },
    {
     "ename": "ValueError",
     "evalue": "No axis named col for object type DataFrame",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mKeyError\u001b[0m                                  Traceback (most recent call last)",
      "\u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\generic.py\u001b[0m in \u001b[0;36m?\u001b[1;34m(cls, axis)\u001b[0m\n\u001b[0;32m    576\u001b[0m             \u001b[1;32mreturn\u001b[0m \u001b[0mcls\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_AXIS_TO_AXIS_NUMBER\u001b[0m\u001b[1;33m[\u001b[0m\u001b[0maxis\u001b[0m\u001b[1;33m]\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    577\u001b[0m         \u001b[1;32mexcept\u001b[0m \u001b[0mKeyError\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 578\u001b[1;33m             \u001b[1;32mraise\u001b[0m \u001b[0mValueError\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33mf\"\u001b[0m\u001b[1;33mNo axis named \u001b[0m\u001b[1;33m{\u001b[0m\u001b[0maxis\u001b[0m\u001b[1;33m}\u001b[0m\u001b[1;33m for object type \u001b[0m\u001b[1;33m{\u001b[0m\u001b[0mcls\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m__name__\u001b[0m\u001b[1;33m}\u001b[0m\u001b[1;33m\"\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[1;31mKeyError\u001b[0m: 'col'",
      "\nDuring handling of the above exception, another exception occurred:\n",
      "\u001b[1;31mValueError\u001b[0m                                Traceback (most recent call last)",
      "\u001b[1;32m~\\AppData\\Local\\Temp\\ipykernel_5252\\1072251557.py\u001b[0m in \u001b[0;36m?\u001b[1;34m()\u001b[0m\n\u001b[0;32m      1\u001b[0m \u001b[0mdf3\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mmake_df\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m'AB'\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;33m[\u001b[0m\u001b[1;36m0\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;36m1\u001b[0m\u001b[1;33m]\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m      2\u001b[0m \u001b[0mdf4\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mmake_df\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m'CD'\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;33m[\u001b[0m\u001b[1;36m0\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;36m1\u001b[0m\u001b[1;33m]\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m----> 3\u001b[1;33m \u001b[0mprint\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mdf3\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m;\u001b[0m \u001b[0mprint\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mdf4\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m;\u001b[0m \u001b[0mprint\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mpd\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mconcat\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m[\u001b[0m\u001b[0mdf3\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mdf4\u001b[0m\u001b[1;33m]\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0maxis\u001b[0m\u001b[1;33m=\u001b[0m\u001b[1;34m'col'\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\reshape\\concat.py\u001b[0m in \u001b[0;36m?\u001b[1;34m(objs, axis, join, ignore_index, keys, levels, names, verify_integrity, sort, copy)\u001b[0m\n\u001b[0;32m    378\u001b[0m             \u001b[0mcopy\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;32mTrue\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    379\u001b[0m     \u001b[1;32melif\u001b[0m \u001b[0mcopy\u001b[0m \u001b[1;32mand\u001b[0m \u001b[0musing_copy_on_write\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    380\u001b[0m         \u001b[0mcopy\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;32mFalse\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    381\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 382\u001b[1;33m     op = _Concatenator(\n\u001b[0m\u001b[0;32m    383\u001b[0m         \u001b[0mobjs\u001b[0m\u001b[1;33m,\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    384\u001b[0m         \u001b[0maxis\u001b[0m\u001b[1;33m=\u001b[0m\u001b[0maxis\u001b[0m\u001b[1;33m,\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    385\u001b[0m         \u001b[0mignore_index\u001b[0m\u001b[1;33m=\u001b[0m\u001b[0mignore_index\u001b[0m\u001b[1;33m,\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\reshape\\concat.py\u001b[0m in \u001b[0;36m?\u001b[1;34m(self, objs, axis, join, keys, levels, names, ignore_index, verify_integrity, copy, sort)\u001b[0m\n\u001b[0;32m    455\u001b[0m             \u001b[0maxis\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mDataFrame\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_get_axis_number\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0maxis\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    456\u001b[0m             \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_is_frame\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;32mFalse\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    457\u001b[0m             \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_is_series\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;32mTrue\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    458\u001b[0m         \u001b[1;32melse\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 459\u001b[1;33m             \u001b[0maxis\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0msample\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_get_axis_number\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0maxis\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m    460\u001b[0m             \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_is_frame\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;32mTrue\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    461\u001b[0m             \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_is_series\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;32mFalse\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    462\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\generic.py\u001b[0m in \u001b[0;36m?\u001b[1;34m(cls, axis)\u001b[0m\n\u001b[0;32m    574\u001b[0m     \u001b[1;32mdef\u001b[0m \u001b[0m_get_axis_number\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mcls\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0maxis\u001b[0m\u001b[1;33m:\u001b[0m \u001b[0mAxis\u001b[0m\u001b[1;33m)\u001b[0m \u001b[1;33m->\u001b[0m \u001b[0mAxisInt\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    575\u001b[0m         \u001b[1;32mtry\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    576\u001b[0m             \u001b[1;32mreturn\u001b[0m \u001b[0mcls\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_AXIS_TO_AXIS_NUMBER\u001b[0m\u001b[1;33m[\u001b[0m\u001b[0maxis\u001b[0m\u001b[1;33m]\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    577\u001b[0m         \u001b[1;32mexcept\u001b[0m \u001b[0mKeyError\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 578\u001b[1;33m             \u001b[1;32mraise\u001b[0m \u001b[0mValueError\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33mf\"\u001b[0m\u001b[1;33mNo axis named \u001b[0m\u001b[1;33m{\u001b[0m\u001b[0maxis\u001b[0m\u001b[1;33m}\u001b[0m\u001b[1;33m for object type \u001b[0m\u001b[1;33m{\u001b[0m\u001b[0mcls\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m__name__\u001b[0m\u001b[1;33m}\u001b[0m\u001b[1;33m\"\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[1;31mValueError\u001b[0m: No axis named col for object type DataFrame"
     ]
    }
   ],
   "source": [
    "df3 = make_df('AB', [0, 1])\n",
    "df4 = make_df('CD', [0, 1])\n",
    "print(df3); print(df4); print(pd.concat([df3, df4], axis='col'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "44083d4b-c066-4682-ab9f-e891ed1c1518",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B\n",
      "0  A0  B0\n",
      "1  A1  B1\n",
      "    A   B\n",
      "0  A2  B2\n",
      "1  A3  B3\n",
      "    A   B\n",
      "0  A0  B0\n",
      "1  A1  B1\n",
      "0  A2  B2\n",
      "1  A3  B3\n"
     ]
    }
   ],
   "source": [
    "x = make_df('AB', [0, 1])\n",
    "y = make_df('AB', [2, 3])\n",
    "y.index = x.index  # make duplicate indices!\n",
    "print(x); print(y); print(pd.concat([x, y]))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "b066dc1c-1271-4387-ae4d-5c3ce0b50a54",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B\n",
      "0  A0  B0\n",
      "1  A1  B1\n",
      "    A   B\n",
      "0  A2  B2\n",
      "1  A3  B3\n",
      "    A   B\n",
      "0  A0  B0\n",
      "1  A1  B1\n",
      "2  A2  B2\n",
      "3  A3  B3\n"
     ]
    }
   ],
   "source": [
    "print(x); print(y); print(pd.concat([x, y], ignore_index=True))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "a290255f-4821-4149-8c02-71855531ace3",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B\n",
      "0  A0  B0\n",
      "1  A1  B1\n",
      "    A   B\n",
      "0  A2  B2\n",
      "1  A3  B3\n",
      "      A   B\n",
      "x 0  A0  B0\n",
      "  1  A1  B1\n",
      "y 0  A2  B2\n",
      "  1  A3  B3\n"
     ]
    }
   ],
   "source": [
    "print(x); print(y); print(pd.concat([x, y], keys=['x', 'y']))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "35b844b6-a29e-4f70-b747-082e70452e7f",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B   C\n",
      "1  A1  B1  C1\n",
      "2  A2  B2  C2\n",
      "    B   C   D\n",
      "3  B3  C3  D3\n",
      "4  B4  C4  D4\n",
      "     A   B   C    D\n",
      "1   A1  B1  C1  NaN\n",
      "2   A2  B2  C2  NaN\n",
      "3  NaN  B3  C3   D3\n",
      "4  NaN  B4  C4   D4\n"
     ]
    }
   ],
   "source": [
    "df5 = make_df('ABC', [1, 2])\n",
    "df6 = make_df('BCD', [3, 4])\n",
    "\n",
    "print(df5)\n",
    "print(df6)\n",
    "print(pd.concat([df5, df6]))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "93231324-c85c-4e25-866f-a7c8b707234b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B   C\n",
      "1  A1  B1  C1\n",
      "2  A2  B2  C2\n",
      "    B   C   D\n",
      "3  B3  C3  D3\n",
      "4  B4  C4  D4\n",
      "    B   C\n",
      "1  B1  C1\n",
      "2  B2  C2\n",
      "3  B3  C3\n",
      "4  B4  C4\n"
     ]
    }
   ],
   "source": [
    "print(df5); print(df6);\n",
    "print(pd.concat([df5, df6], join='inner'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "25e9bed9-c459-446e-addc-80234e4f6121",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B   C\n",
      "1  A1  B1  C1\n",
      "2  A2  B2  C2\n",
      "    B   C   D\n",
      "3  B3  C3  D3\n",
      "4  B4  C4  D4\n"
     ]
    },
    {
     "ename": "TypeError",
     "evalue": "concat() got an unexpected keyword argument 'join_axes'",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mTypeError\u001b[0m                                 Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[20], line 2\u001b[0m\n\u001b[0;32m      1\u001b[0m \u001b[38;5;28mprint\u001b[39m(df5); \u001b[38;5;28mprint\u001b[39m(df6);\n\u001b[1;32m----> 2\u001b[0m \u001b[38;5;28mprint\u001b[39m(\u001b[43mpd\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mconcat\u001b[49m\u001b[43m(\u001b[49m\u001b[43m[\u001b[49m\u001b[43mdf5\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[43mdf6\u001b[49m\u001b[43m]\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[43mjoin_axes\u001b[49m\u001b[38;5;241;43m=\u001b[39;49m\u001b[43m[\u001b[49m\u001b[43mdf5\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mcolumns\u001b[49m\u001b[43m]\u001b[49m\u001b[43m)\u001b[49m)\n",
      "\u001b[1;31mTypeError\u001b[0m: concat() got an unexpected keyword argument 'join_axes'"
     ]
    }
   ],
   "source": [
    "print(df5); print(df6);\n",
    "print(pd.concat([df5, df6], join_axes=[df5.columns]))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "17806bf1-397b-4e1f-8543-73d48c22da45",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    A   B\n",
      "1  A1  B1\n",
      "2  A2  B2\n",
      "    A   B\n",
      "3  A3  B3\n",
      "4  A4  B4\n"
     ]
    },
    {
     "ename": "AttributeError",
     "evalue": "'DataFrame' object has no attribute 'append'",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mAttributeError\u001b[0m                            Traceback (most recent call last)",
      "\u001b[1;32m~\\AppData\\Local\\Temp\\ipykernel_5252\\3875926826.py\u001b[0m in \u001b[0;36m?\u001b[1;34m()\u001b[0m\n\u001b[1;32m----> 1\u001b[1;33m \u001b[0mprint\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mdf1\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m;\u001b[0m \u001b[0mprint\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mdf2\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m;\u001b[0m \u001b[0mprint\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mdf1\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mappend\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mdf2\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[1;32m~\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\pandas\\core\\generic.py\u001b[0m in \u001b[0;36m?\u001b[1;34m(self, name)\u001b[0m\n\u001b[0;32m   6295\u001b[0m             \u001b[1;32mand\u001b[0m \u001b[0mname\u001b[0m \u001b[1;32mnot\u001b[0m \u001b[1;32min\u001b[0m \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_accessors\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m   6296\u001b[0m             \u001b[1;32mand\u001b[0m \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_info_axis\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m_can_hold_identifiers_and_holds_name\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mname\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m   6297\u001b[0m         \u001b[1;33m)\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m   6298\u001b[0m             \u001b[1;32mreturn\u001b[0m \u001b[0mself\u001b[0m\u001b[1;33m[\u001b[0m\u001b[0mname\u001b[0m\u001b[1;33m]\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m-> 6299\u001b[1;33m         \u001b[1;32mreturn\u001b[0m \u001b[0mobject\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0m__getattribute__\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mself\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mname\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[1;31mAttributeError\u001b[0m: 'DataFrame' object has no attribute 'append'"
     ]
    }
   ],
   "source": [
    " print(df1); print(df2); print(df1.append(df2))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "49f9a144-f0ac-4a49-b82a-45ced9fa4b15",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Combining Datasets: Merge and Join\n"
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
   "version": "3.12.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
