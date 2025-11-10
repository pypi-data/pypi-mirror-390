def prac6():
    code = '''
#pip install in jupyter notebook
pip install pyspark 
pip install findspark


#if error persists
# ANACONDA PROMPT do following and then again do all steps from start 
pip uninstall pyspark -y
pip uninstall py4j -y
pip install pyspark==3.3.1
conda create -n pyspark-env python=3.10 -y
conda activate pyspark-env
pip install pyspark==3.3.1 findspark
jupyter notebook #launch jupyter notebook from anaconda prompt



#if error :
import os
print(os.environ.get("JAVA_HOME")) #see if java home is set or not in device
#set java home temporarily
import os
os.environ["JAVA_HOME"] = r"C:\Java\jdk1.8.0_121"
os.environ["PATH"] = os.environ["JAVA_HOME"] + r"\bin;" + os.environ["PATH"]
!java -version


#findspark initialization
import findspark
findspark.init()

#Importing PySpark
from pyspark.sql import SparkSession


#Create or Get a Spark
spark=SparkSession.builder.appName("PySpart-Get-Started").getOrCreate()

#Create Sample data
data = [("Alice",25),("Bob",30),("Charlie",35)]

#Convert to DataFrame
df = spark.createDataFrame(data, ["Name","Age"])
df.show()

# Selecting only the "Name" column from df
only_name = df.select("Name")
only_name.show()

#Incease age by 1
age_mod = df.withColumn("Age",df["Age"]+1)
#selecting name and updated age
age_select = age_mod.select("Name","Age")
age_select.show()

#Calculate avg age 
age_average = df.agg({"Age":"avg"})
age_average.show()

#Select only the first row and display it.
df.limit(1).show()

#Saving age data in csv, paraquet, json
save_data = age_select.write.csv("age_data.csv")
save_data_parquet = age_select.write.parquet("age_data.parquet")
save_data_json = age_select.write.json("age_data.json")
  '''
    return code