{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "0277123f-b689-4974-9dd8-90f13e449430",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Combining Datasets: Merge and Join"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "03dc4f77-84bf-49eb-a6bc-31dcec0e6571",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  employee        group\n",
      "0      Bob   Accounting\n",
      "1     Jake  Engineering\n",
      "2     Lisa  Engineering\n",
      "3      Sue           HR\n",
      "  employee  hire_date\n",
      "0     Lisa       2004\n",
      "1      Bob       2008\n",
      "2     Jake       2012\n",
      "3      Sue       2014\n"
     ]
    }
   ],
   "source": [
    "import pandas as pd\n",
    "\n",
    "df1 = pd.DataFrame({'employee': ['Bob', 'Jake', 'Lisa', 'Sue'],\n",
    "                    'group': ['Accounting', 'Engineering', 'Engineering', 'HR']})\n",
    "df2 = pd.DataFrame({'employee': ['Lisa', 'Bob', 'Jake', 'Sue'],\n",
    "                    'hire_date': [2004, 2008, 2012, 2014]})\n",
    "\n",
    "print(df1)\n",
    "print(df2)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "3b7adc6d-2261-4c55-9834-e0b05e8d4691",
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
       "      <th>employee</th>\n",
       "      <th>group</th>\n",
       "      <th>hire_date</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Bob</td>\n",
       "      <td>Accounting</td>\n",
       "      <td>2008</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Jake</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>2012</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Lisa</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>2004</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Sue</td>\n",
       "      <td>HR</td>\n",
       "      <td>2014</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  employee        group  hire_date\n",
       "0      Bob   Accounting       2008\n",
       "1     Jake  Engineering       2012\n",
       "2     Lisa  Engineering       2004\n",
       "3      Sue           HR       2014"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " df3 = pd.merge(df1, df2)\n",
    " df3"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "e593e641-83dc-41af-98f2-d492333be303",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  employee        group  hire_date\n",
      "0      Bob   Accounting       2008\n",
      "1     Jake  Engineering       2012\n",
      "2     Lisa  Engineering       2004\n",
      "3      Sue           HR       2014\n",
      "         group supervisor\n",
      "0   Accounting      Carly\n",
      "1  Engineering      Guido\n",
      "2           HR      Steve\n",
      "  employee        group  hire_date supervisor\n",
      "0      Bob   Accounting       2008      Carly\n",
      "1     Jake  Engineering       2012      Guido\n",
      "2     Lisa  Engineering       2004      Guido\n",
      "3      Sue           HR       2014      Steve\n"
     ]
    }
   ],
   "source": [
    "#Many-to-one joins\n",
    "df4 = pd.DataFrame({'group': ['Accounting', 'Engineering', 'HR'],\n",
    " 'supervisor': ['Carly', 'Guido', 'Steve']})\n",
    "print(df3); print(df4); print(pd.merge(df3, df4))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "01bddbb5-25d2-4bd5-bcb6-60b77dcf58b9",
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
       "      <th>employee</th>\n",
       "      <th>group</th>\n",
       "      <th>hire_date</th>\n",
       "      <th>supervisor</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Bob</td>\n",
       "      <td>Accounting</td>\n",
       "      <td>2008</td>\n",
       "      <td>Carly</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Jake</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>2012</td>\n",
       "      <td>Guido</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Lisa</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>2004</td>\n",
       "      <td>Guido</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Sue</td>\n",
       "      <td>HR</td>\n",
       "      <td>2014</td>\n",
       "      <td>Steve</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  employee        group  hire_date supervisor\n",
       "0      Bob   Accounting       2008      Carly\n",
       "1     Jake  Engineering       2012      Guido\n",
       "2     Lisa  Engineering       2004      Guido\n",
       "3      Sue           HR       2014      Steve"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.merge(df3, df4)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "b8ca21b1-4295-4219-91e8-ef4cdf46ea5d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  employee        group\n",
      "0      Bob   Accounting\n",
      "1     Jake  Engineering\n",
      "2     Lisa  Engineering\n",
      "3      Sue           HR\n",
      "         group        skills\n",
      "0   Accounting          math\n",
      "1   Accounting  spreadsheets\n",
      "2  Engineering        coding\n",
      "3  Engineering         linux\n",
      "4           HR  spreadsheets\n",
      "5           HR  organization\n",
      "  employee        group        skills\n",
      "0      Bob   Accounting          math\n",
      "1      Bob   Accounting  spreadsheets\n",
      "2     Jake  Engineering        coding\n",
      "3     Jake  Engineering         linux\n",
      "4     Lisa  Engineering        coding\n",
      "5     Lisa  Engineering         linux\n",
      "6      Sue           HR  spreadsheets\n",
      "7      Sue           HR  organization\n"
     ]
    }
   ],
   "source": [
    "import pandas as pd\n",
    "\n",
    "# df1 from earlier\n",
    "df1 = pd.DataFrame({'employee': ['Bob', 'Jake', 'Lisa', 'Sue'],\n",
    "                    'group': ['Accounting', 'Engineering', 'Engineering', 'HR']})\n",
    "\n",
    "# Corrected df5\n",
    "df5 = pd.DataFrame({'group': ['Accounting', 'Accounting',\n",
    "                              'Engineering', 'Engineering',\n",
    "                              'HR', 'HR'],\n",
    "                    'skills': ['math', 'spreadsheets',\n",
    "                               'coding', 'linux',\n",
    "                               'spreadsheets', 'organization']})\n",
    "\n",
    "# Many-to-many merge\n",
    "print(df1)\n",
    "print(df5)\n",
    "print(pd.merge(df1, df5))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "1f2bef56-182a-4edf-a18a-98f2ebb4d65e",
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
       "      <th>employee</th>\n",
       "      <th>group</th>\n",
       "      <th>skills</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Bob</td>\n",
       "      <td>Accounting</td>\n",
       "      <td>math</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Bob</td>\n",
       "      <td>Accounting</td>\n",
       "      <td>spreadsheets</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Jake</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>coding</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Jake</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>linux</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>Lisa</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>coding</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>Lisa</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>linux</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6</th>\n",
       "      <td>Sue</td>\n",
       "      <td>HR</td>\n",
       "      <td>spreadsheets</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>7</th>\n",
       "      <td>Sue</td>\n",
       "      <td>HR</td>\n",
       "      <td>organization</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  employee        group        skills\n",
       "0      Bob   Accounting          math\n",
       "1      Bob   Accounting  spreadsheets\n",
       "2     Jake  Engineering        coding\n",
       "3     Jake  Engineering         linux\n",
       "4     Lisa  Engineering        coding\n",
       "5     Lisa  Engineering         linux\n",
       "6      Sue           HR  spreadsheets\n",
       "7      Sue           HR  organization"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " pd.merge(df1, df5)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "c1b26950-214d-4496-8cf9-81954ee85fca",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  employee        group\n",
      "0      Bob   Accounting\n",
      "1     Jake  Engineering\n",
      "2     Lisa  Engineering\n",
      "3      Sue           HR\n",
      "  employee  hire_date\n",
      "0     Lisa       2004\n",
      "1      Bob       2008\n",
      "2     Jake       2012\n",
      "3      Sue       2014\n",
      "  employee        group  hire_date\n",
      "0      Bob   Accounting       2008\n",
      "1     Jake  Engineering       2012\n",
      "2     Lisa  Engineering       2004\n",
      "3      Sue           HR       2014\n"
     ]
    }
   ],
   "source": [
    "#Speciication of the Merge Key\n",
    "#The on keyword\n",
    "print(df1); print(df2); print(pd.merge(df1, df2, on='employee'))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "45a089a4-f287-4003-abf9-966ad50ed071",
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
       "      <th>employee</th>\n",
       "      <th>group</th>\n",
       "      <th>hire_date</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Bob</td>\n",
       "      <td>Accounting</td>\n",
       "      <td>2008</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Jake</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>2012</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Lisa</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>2004</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Sue</td>\n",
       "      <td>HR</td>\n",
       "      <td>2014</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  employee        group  hire_date\n",
       "0      Bob   Accounting       2008\n",
       "1     Jake  Engineering       2012\n",
       "2     Lisa  Engineering       2004\n",
       "3      Sue           HR       2014"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.merge(df1, df2, on='employee')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "05617a31-e8b2-48e3-bc77-b1b965f3fcd5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "  employee        group\n",
      "0      Bob   Accounting\n",
      "1     Jake  Engineering\n",
      "2     Lisa  Engineering\n",
      "3      Sue           HR\n",
      "   name  salary\n",
      "0   Bob   70000\n",
      "1  Jake   80000\n",
      "2  Lisa  120000\n",
      "3   Sue   90000\n",
      "  employee        group  name  salary\n",
      "0      Bob   Accounting   Bob   70000\n",
      "1     Jake  Engineering  Jake   80000\n",
      "2     Lisa  Engineering  Lisa  120000\n",
      "3      Sue           HR   Sue   90000\n"
     ]
    }
   ],
   "source": [
    "# The left_on and right_on keywords\n",
    "df3 = pd.DataFrame({'name': ['Bob', 'Jake', 'Lisa', 'Sue'],\n",
    " 'salary': [70000, 80000, 120000, 90000]})\n",
    "print(df1); print(df3);\n",
    "print(pd.merge(df1, df3, left_on=\"employee\", right_on=\"name\"))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "7c8b5949-bf53-4971-b439-aaac86d3c312",
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
       "      <th>employee</th>\n",
       "      <th>group</th>\n",
       "      <th>name</th>\n",
       "      <th>salary</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Bob</td>\n",
       "      <td>Accounting</td>\n",
       "      <td>Bob</td>\n",
       "      <td>70000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Jake</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>Jake</td>\n",
       "      <td>80000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Lisa</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>Lisa</td>\n",
       "      <td>120000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Sue</td>\n",
       "      <td>HR</td>\n",
       "      <td>Sue</td>\n",
       "      <td>90000</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  employee        group  name  salary\n",
       "0      Bob   Accounting   Bob   70000\n",
       "1     Jake  Engineering  Jake   80000\n",
       "2     Lisa  Engineering  Lisa  120000\n",
       "3      Sue           HR   Sue   90000"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.merge(df1, df3, left_on=\"employee\", right_on=\"name\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "97deb4d4-b7f3-4b7b-84ce-1ab024d22a1e",
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
       "      <th>employee</th>\n",
       "      <th>group</th>\n",
       "      <th>salary</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Bob</td>\n",
       "      <td>Accounting</td>\n",
       "      <td>70000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Jake</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>80000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Lisa</td>\n",
       "      <td>Engineering</td>\n",
       "      <td>120000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Sue</td>\n",
       "      <td>HR</td>\n",
       "      <td>90000</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "  employee        group  salary\n",
       "0      Bob   Accounting   70000\n",
       "1     Jake  Engineering   80000\n",
       "2     Lisa  Engineering  120000\n",
       "3      Sue           HR   90000"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.merge(df1, df3, left_on=\"employee\", right_on=\"name\").drop('name', axis=1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "a5cf7cf7-eee8-4c51-8406-c1ee6e1ddd2d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                group\n",
      "employee             \n",
      "Bob        Accounting\n",
      "Jake      Engineering\n",
      "Lisa      Engineering\n",
      "Sue                HR\n",
      "          hire_date\n",
      "employee           \n",
      "Lisa           2004\n",
      "Bob            2008\n",
      "Jake           2012\n",
      "Sue            2014\n"
     ]
    }
   ],
   "source": [
    "#The left_index and right_index keywords\n",
    "df1a = df1.set_index('employee')\n",
    "df2a = df2.set_index('employee')\n",
    "print(df1a); print(df2a)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "585ba1a3-98fc-4866-baf4-2e4f5c2fcf7b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                group\n",
      "employee             \n",
      "Bob        Accounting\n",
      "Jake      Engineering\n",
      "Lisa      Engineering\n",
      "Sue                HR\n",
      "          hire_date\n",
      "employee           \n",
      "Lisa           2004\n",
      "Bob            2008\n",
      "Jake           2012\n",
      "Sue            2014\n",
      "                group  hire_date\n",
      "employee                        \n",
      "Bob        Accounting       2008\n",
      "Jake      Engineering       2012\n",
      "Lisa      Engineering       2004\n",
      "Sue                HR       2014\n"
     ]
    }
   ],
   "source": [
    "print(df1a); print(df2a);\n",
    "print(pd.merge(df1a, df2a, left_index=True, right_index=True))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "ff04a499-75ef-4a2d-adc1-c891d87d0d39",
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
       "      <th>group</th>\n",
       "      <th>hire_date</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>employee</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>Bob</th>\n",
       "      <td>Accounting</td>\n",
       "      <td>2008</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Jake</th>\n",
       "      <td>Engineering</td>\n",
       "      <td>2012</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Lisa</th>\n",
       "      <td>Engineering</td>\n",
       "      <td>2004</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Sue</th>\n",
       "      <td>HR</td>\n",
       "      <td>2014</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                group  hire_date\n",
       "employee                        \n",
       "Bob        Accounting       2008\n",
       "Jake      Engineering       2012\n",
       "Lisa      Engineering       2004\n",
       "Sue                HR       2014"
      ]
     },
     "execution_count": 18,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    " pd.merge(df1a, df2a, left_index=True, right_index=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "534ff9b9-8296-4003-8422-6dbc348adc6f",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                group\n",
      "employee             \n",
      "Bob        Accounting\n",
      "Jake      Engineering\n",
      "Lisa      Engineering\n",
      "Sue                HR\n",
      "          hire_date\n",
      "employee           \n",
      "Lisa           2004\n",
      "Bob            2008\n",
      "Jake           2012\n",
      "Sue            2014\n",
      "                group  hire_date\n",
      "employee                        \n",
      "Bob        Accounting       2008\n",
      "Jake      Engineering       2012\n",
      "Lisa      Engineering       2004\n",
      "Sue                HR       2014\n"
     ]
    }
   ],
   "source": [
    "print(df1a); print(df2a); print(df1a.join(df2a))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "68e87dfd-ae69-4f5f-8a19-3422d4b0269b",
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
       "      <th>group</th>\n",
       "      <th>hire_date</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>employee</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>Bob</th>\n",
       "      <td>Accounting</td>\n",
       "      <td>2008</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Jake</th>\n",
       "      <td>Engineering</td>\n",
       "      <td>2012</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Lisa</th>\n",
       "      <td>Engineering</td>\n",
       "      <td>2004</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>Sue</th>\n",
       "      <td>HR</td>\n",
       "      <td>2014</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                group  hire_date\n",
       "employee                        \n",
       "Bob        Accounting       2008\n",
       "Jake      Engineering       2012\n",
       "Lisa      Engineering       2004\n",
       "Sue                HR       2014"
      ]
     },
     "execution_count": 20,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df1a.join(df2a)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "31a8304f-f143-4621-bbee-c774160dd570",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                group\n",
      "employee             \n",
      "Bob        Accounting\n",
      "Jake      Engineering\n",
      "Lisa      Engineering\n",
      "Sue                HR\n",
      "   name  salary\n",
      "0   Bob   70000\n",
      "1  Jake   80000\n",
      "2  Lisa  120000\n",
      "3   Sue   90000\n",
      "         group  name  salary\n",
      "0   Accounting   Bob   70000\n",
      "1  Engineering  Jake   80000\n",
      "2  Engineering  Lisa  120000\n",
      "3           HR   Sue   90000\n"
     ]
    }
   ],
   "source": [
    "print(df1a); print(df3);\n",
    "print(pd.merge(df1a, df3, left_index=True, right_on='name'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "84466563-32ac-4a81-9726-0538ff300f58",
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
       "      <th>group</th>\n",
       "      <th>name</th>\n",
       "      <th>salary</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Accounting</td>\n",
       "      <td>Bob</td>\n",
       "      <td>70000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Engineering</td>\n",
       "      <td>Jake</td>\n",
       "      <td>80000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Engineering</td>\n",
       "      <td>Lisa</td>\n",
       "      <td>120000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>HR</td>\n",
       "      <td>Sue</td>\n",
       "      <td>90000</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "         group  name  salary\n",
       "0   Accounting   Bob   70000\n",
       "1  Engineering  Jake   80000\n",
       "2  Engineering  Lisa  120000\n",
       "3           HR   Sue   90000"
      ]
     },
     "execution_count": 22,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pd.merge(df1a, df3, left_index=True, right_on='name')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "87a547fa-3fcb-4fd6-972e-9d589df3d8e3",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    name   food\n",
      "0  Peter   fish\n",
      "1   Paul  beans\n",
      "2   Mary  bread\n",
      "     name drink\n",
      "0    Mary  wine\n",
      "1  Joseph  beer\n",
      "   name   food drink\n",
      "0  Mary  bread  wine\n"
     ]
    }
   ],
   "source": [
    "#Specifying Set Arithmetic for Joins\n",
    "df6 = pd.DataFrame({'name': ['Peter', 'Paul', 'Mary'],\n",
    "                            'food': ['fish', 'beans', 'bread']},\n",
    "                           columns=['name', 'food'])\n",
    "df7 = pd.DataFrame({'name': ['Mary', 'Joseph'],\n",
    "                            'drink': ['wine', 'beer']},\n",
    "                           columns=['name', 'drink'])\n",
    "print(df6); print(df7); print(pd.merge(df6, df7))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "981e59f4-a9b0-43a8-93a2-0b3690232346",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    name   food\n",
      "0  Peter   fish\n",
      "1   Paul  beans\n",
      "2   Mary  bread\n",
      "     name drink\n",
      "0    Mary  wine\n",
      "1  Joseph  beer\n",
      "     name   food drink\n",
      "0  Joseph    NaN  beer\n",
      "1    Mary  bread  wine\n",
      "2    Paul  beans   NaN\n",
      "3   Peter   fish   NaN\n"
     ]
    }
   ],
   "source": [
    "print(df6); print(df7); print(pd.merge(df6, df7, how='outer'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "200de952-7217-4b6a-8e88-bb8eaf3453b0",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "    name   food\n",
      "0  Peter   fish\n",
      "1   Paul  beans\n",
      "2   Mary  bread\n",
      "     name drink\n",
      "0    Mary  wine\n",
      "1  Joseph  beer\n",
      "    name   food drink\n",
      "0  Peter   fish   NaN\n",
      "1   Paul  beans   NaN\n",
      "2   Mary  bread  wine\n"
     ]
    }
   ],
   "source": [
    "print(df6); print(df7); print(pd.merge(df6, df7, how='left'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f72e5ddd-fc74-47f2-9aeb-5a15b610b669",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Overlapping Column Names: The suixes Keyword"
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
