import sys
import os
import pandas as pd

# Add the parent directory to Python path to use local package source
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import duckrun

# Analyze multiple schemas/tables
conn = duckrun.connect("tmp/data.lakehouse/spark_vorder")

# Analyze tables - now returns long format automatically
result = conn.rle("summary")
print(result)
conn.close()

