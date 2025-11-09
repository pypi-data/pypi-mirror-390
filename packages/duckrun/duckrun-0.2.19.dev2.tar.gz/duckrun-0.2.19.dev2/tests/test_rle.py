import duckrun

# Test RLE integration
con = duckrun.connect("tmp/data.lakehouse/unsorted")

# Test smart mode on calendar table
print("Testing RLE smart mode on calendar table...")
result = con.rle("calendar", "full")
print("\nTop 5 best orderings:")
print(result[['sort_order', 'columns_used', 'total_rle', 'estimation_method']].head())
