from src.rag_engine import _handle_category_attribute_query, _handle_category_query

# Test 1: "show all hybrid fund nav" - should be handled by attribute handler
query1 = "show all hybrid fund nav"
result1_cat = _handle_category_query(query1)
result1_attr = _handle_category_attribute_query(query1)

print("Test 1: show all hybrid fund nav")
print(f"  Category handler: {'Handled' if result1_cat else 'None (correct)'}")
print(f"  Attribute handler: {'Handled (correct)' if result1_attr else 'None'}")
if result1_attr:
    print(f"  Answer preview: {result1_attr['answer'][:150]}...")
print()

# Test 2: "show all hybrid funds" - should be handled by category handler
query2 = "show all hybrid funds"
result2_cat = _handle_category_query(query2)
result2_attr = _handle_category_attribute_query(query2)

print("Test 2: show all hybrid funds")
print(f"  Category handler: {'Handled (correct)' if result2_cat else 'None'}")
print(f"  Attribute handler: {'Handled' if result2_attr else 'None (correct)'}")
if result2_cat:
    print(f"  Answer preview: {result2_cat['answer'][:150]}...")
print()

# Test 3: "show nav of equity funds" - should be handled by attribute handler
query3 = "show nav of equity funds"
result3_cat = _handle_category_query(query3)
result3_attr = _handle_category_attribute_query(query3)

print("Test 3: show nav of equity funds")
print(f"  Category handler: {'Handled' if result3_cat else 'None (correct)'}")
print(f"  Attribute handler: {'Handled (correct)' if result3_attr else 'None'}")
if result3_attr:
    print(f"  Answer preview: {result3_attr['answer'][:150]}...")
