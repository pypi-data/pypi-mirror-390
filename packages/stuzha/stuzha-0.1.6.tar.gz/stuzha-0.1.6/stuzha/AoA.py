from colorama import Fore, Style, init

init(autoreset=True)

def pk_1():
    print(Fore.RED + '''

#Quick Sort

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

arr = [3, 6, 8, 10, 1, 2, 11]
sorted_arr = quick_sort(arr)
print(sorted_arr)


#Bubble Sort

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

arr = [64, 34, 25, 12, 22, 11, 90]
bubble_sort(arr)
print(arr)


#Shell Sort

def shell_sort(arr):
    n = len(arr)
    gap = n // 2
    print(f'Value of n: {n}')
   
    while gap > 0:
        for i in range(gap, n):
            print(f'i: {i}')
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        print(gap)
        gap //= 2  

arr = [64, 34, 25, 12, 22, 11, 90]
shell_sort(arr)
print(arr)


#Merge Sort

def merge_sort(arr):
   if len(arr) <= 1:
       return arr
   mid = len(arr) // 2
   left = merge_sort(arr[:mid])
   right = merge_sort(arr[mid:])
   return merge(left, right)

def merge(left, right):
   result = []
   i = j = 0
   while i < len(left) and j < len(right):
       if left[i] <= right[j]:
           result.append(left[i])
           i += 1
       else:
           result.append(right[j])
           j += 1
   result.extend(left[i:])
   result.extend(right[j:])
   return result

arr = [64, 34, 25, 12, 22, 11, 90]
sorted_arr = merge_sort(arr)
print(sorted_arr)

          
#Selection Sort

def selection_sort(arr):
   n = len(arr)
   for i in range(n):
       min_idx = i
       for j in range(i+1, n):
           if arr[j] < arr[min_idx]:
               min_idx = j
       arr[i], arr[min_idx] = arr[min_idx], arr[i]

arr = [64, 34, 25, 12, 22, 11, 90]
selection_sort(arr)
print(arr)

          ''')

def pk_2():
    print(Fore.RED + '''
          
#Matrix Multiplication

A = [
   [1, 2, 3],
   [4, 5, 6]
]

B = [
   [7, 8],
   [9, 10],
   [11, 12]
]

result = [
   [0, 0],
   [0, 0]
]

for i in range(len(A)): 
   for j in range(len(B[0])): 
       for k in range(len(B)): 
           result[i][j] += A[i][k] * B[k][j]

print("Result of Matrix Multiplication:")
for row in result:
   print(row)



#Strassen Matrix Multiplication

def strassen(a, b):
   a11 = a[0][0]
   a12 = a[0][1]
   a21 = a[1][0]
   a22 = a[1][1]

   b11 = b[0][0]
   b12 = b[0][1]
   b21 = b[1][0]
   b22 = b[1][1]

   m1 = (a11 + a22) * (b11 + b22)
   m2 = (a21 + a22) * b11
   m3 = a11 * (b12 - b22)
   m4 = a22 * (b21 - b11)
   m5 = (a11 + a12) * b22
   m6 = (a21 - a11) * (b11 + b12)
   m7 = (a12 - a22) * (b21 + b22)

   c11 = m1 + m4 - m5 + m7
   c12 = m3 + m5
   c21 = m2 + m4
   c22 = m1 - m2 + m3 + m6

   return [
       [c11, c12],
       [c21, c22]
   ]

A = [
   [1, 2],
   [3, 4]
]

B = [
   [5, 6],
   [7, 8]
]
result = strassen(A, B)
print("Result of Strassen Matrix Multiplication:")
for row in result:
   print(row)
   
          ''')

def pk_3():
    print(Fore.RED + '''
          
          
#Hiring Problem

import random
# Set the number of candidates
N = 10

candidates = [{"id": i, "quality": random.randint(0, 100)} for i in range(N)]

def hire_candidates(threshold):
   print("\nCandidates:")
   for candidate in candidates:
       print(f"[id: {candidate['id']}, quality: {candidate['quality']}]")
  
   hired = None
   for candidate in candidates:
       if candidate['quality'] >= threshold:
           hired = candidate
           break  # Hire the first candidate who meets the threshold
  
   if hired:
       print("\nHired Candidate:")
       print(f"[id: {hired['id']}, quality: {hired['quality']}]")
   else:
       print("\nNo candidate meets the threshold.")

# Main program
try:
   # Take threshold input from the user
   threshold = int(input("Enter threshold (0-100): "))
   if 0 <= threshold <= 100:
       hire_candidates(threshold)
   else:
       print("Please enter a threshold between 0 and 100.")
except ValueError:
   print("Invalid input. Please enter a numeric value.")


#Second Hiring Problem

import random
# Set the number of candidates
N = 10 
candidates = [{"id": i, "quality": random.randint(0, 100)} for i in range(N)]

def hire_candidates(num_to_reject):
   rejected_candidates = candidates[:num_to_reject]
   if rejected_candidates:
       threshold = max(candidate['quality'] for candidate in rejected_candidates)
   else:
       threshold = 0 
   print(f"\nQuality threshold set to: {threshold}")
   remaining_candidates = candidates[num_to_reject:]
   print("\nRejected Candidates:")
   for candidate in rejected_candidates:
       print(f"[id: {candidate['id']}, quality: {candidate['quality']}]")
   print("\nRemaining Candidates (Eligible for Hiring):")
   for candidate in remaining_candidates:
       print(f"[id: {candidate['id']}, quality: {candidate['quality']}]")
   hired = None
   for candidate in remaining_candidates:
       if candidate['quality'] >= threshold:
           hired = candidate
           break  # Hire the first candidate who meets or exceeds the threshold
   if hired:
       print("\nHired Candidate:")
       print(f"[id: {hired['id']}, quality: {hired['quality']}]")
   else:
       print("\nNo candidate meets the threshold.")

print(f"Number of candidates: {len(candidates)}")
try:
   num_to_reject = int(input("\nEnter the number of candidates to reject: "))
   if 0 <= num_to_reject <= N:
       hire_candidates(num_to_reject)
   else:
       print(f"Please enter a number between 0 and {N}.")
except ValueError:
   print("Invalid input. Please enter a numeric value.")
          ''')
    
def pk_4():
    print(Fore.RED + '''
          
#Radix Sort

def radix_sort(arr):
   exp = 1
   max_num = max(arr)
   while max_num // exp > 0:
       count = [0] * 10
       output = [0] * len(arr)

       for num in arr:
           count[(num // exp) % 10] += 1
       for i in range(1, 10):
           count[i] += count[i - 1]
       for num in reversed(arr):
           digit = (num // exp) % 10
           output[count[digit] - 1] = num
           count[digit] -= 1
       arr[:] = output
       exp *= 10

numbers = [20, 2, 7, 15, 1, 6, 8]
radix_sort(numbers)
print(f'\n{numbers}\n')


#Counting Sort

def counting_sort(arr):
   max_val = max(arr)
   min_val = min(arr)
   range_of_elements = max_val - min_val + 1
   count = [0] * range_of_elements
   output = [0] * len(arr)
   for num in arr:
       count[num - min_val] += 1
   for i in range(1, range_of_elements):
       count[i] += count[i - 1]
   for num in reversed(arr):
       output[count[num - min_val] - 1] = num
       count[num - min_val] -= 1
   for i in range(len(arr)):
       arr[i] = output[i]

numbers = [20, 2, 7, 15, 1, 6, 8]
counting_sort(numbers)
print(f'\n{numbers}\n')


#Bucket Sort

def bucket_sort(arr):
   n = len(arr)
   if n == 0:
       return
   buckets = [[] for _ in range(n)]
   min_val, max_val = min(arr), max(arr)
   range_val = (max_val - min_val) / n
   for num in arr:
       index = int((num - min_val) / range_val)
       if index == n: 
           index -= 1
       buckets[index].append(num)
   arr.clear()
   for bucket in buckets:
       bucket.sort()
       arr.extend(bucket)

numbers = [0.20, 0.2, 0.7, 0.15, 0.1, 0.6, 0.8]
bucket_sort(numbers)
print(f'\n{numbers}\n')
          ''')

def pk_5():
    print(Fore.RED + '''
          
#K-smallest and largest element

import heapq
def kthSmallest(arr, K):
   max_heap = []
   for num in arr:
       heapq.heappush(max_heap, -num)
       if len(max_heap) > K:
           heapq.heappop(max_heap)
   return -max_heap[0]

def kthLargest(arr, K):
   min_heap = []
   for num in arr:
       heapq.heappush(min_heap, num)
       if len(min_heap) > K:
           heapq.heappop(min_heap)
   return min_heap[0]

if __name__ == "__main__":
   arr = [2, 6, 3, 1, 21, 25, 8, 13, 69, 5]
   K = 4
   print(f"Array: {arr}")
   print(f"K = {K}")
   print(f"Kth smallest element: {kthSmallest(arr, K)}")
   print(f"Kth largest element: {kthLargest(arr, K)}")


#Median of Medians 

def median_of_medians(arr, k):
   sublists = [arr[i:i+5] for i in range(0, len(arr), 5)]
  
   medians = [sorted(sublist)[len(sublist)//2] for sublist in sublists]
  
   # Find the median of the medians recursively
   if len(medians) <= 5:
       pivot = sorted(medians)[len(medians)//2]
   else:
       pivot = median_of_medians(medians, len(medians)//2)
  
   # Partition the array around the pivot
   low = [el for el in arr if el < pivot]
   high = [el for el in arr if el > pivot]
   pivots = [el for el in arr if el == pivot]
  
   # Select the kth element
   if k < len(low):
       return median_of_medians(low, k)
   elif k < len(low) + len(pivots):
       return pivot
   else:
       return median_of_medians(high, k - len(low) - len(pivots))

arr = [2, 6, 3, 1, 21, 25, 8, 13, 69, 5]
k = len(arr) // 2 
median_value = median_of_medians(arr, k)
print(f"The {k}th smallest element is: {median_value}")
          ''')
    
def pk_6():
    print(Fore.RED + '''
          
#Rod cutting problem

def rod_cutting():
    n = int(input("Enter the length of the rod: "))
    prices = [int(input(f"Price for length {i+1}: ")) for i in range(n)]

    dp = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            dp[i][j] = max(dp[i - 1][j], prices[i - 1] + dp[i][j - i]) if i <= j else dp[i - 1][j]

    print("\nProfit Matrix:")
    for row in dp:
        print("".join(f"{v:>8}" for v in row))

    print(f"\nMaximum obtained value is {dp[n][n]}")

    pieces, i, j = [], n, n
    while j:
        if dp[i][j] == dp[i - 1][j]:
            i -= 1
        else:
            pieces.append(i)
            j -= i

    print("\nPieces used for maximum profit:")
    print(" ".join(map(str, pieces)))

if __name__ == "__main__":
    rod_cutting()

          ''')
    
def pk_7():
    print(Fore.RED + '''
          
#DP - LCS

def lcs(X, Y):
   m, n = len(X), len(Y)  
   dp = [[0] * (n + 1) for _ in range(m + 1)]
   for i in range(1, m + 1):
       for j in range(1, n + 1):
           if X[i - 1] == Y[j - 1]:
               dp[i][j] = dp[i - 1][j - 1] + 1
           else:
               dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
  
   lcs_string = []
   i, j = m, n
   while i > 0 and j > 0:
       if X[i - 1] == Y[j - 1]:
           lcs_string.append(X[i - 1])
           i -= 1
           j -= 1
       elif dp[i - 1][j] > dp[i][j - 1]:
           i -= 1
       else:
           j -= 1  
   return ''.join(reversed(lcs_string))

if __name__ == "__main__":
   str1 = input("\nEnter the first string: ")
   str2 = input("Enter the second string: ")
   print(f"The Longest Common Subsequence is: {lcs(str1, str2)}")
   print(f"Length: {len(lcs(str1, str2))} \n")
          

#DP - MCM

def matrix_chain_order(p):
   n = len(p) - 1 
   m = [[0] * n for _ in range(n)]
   s = [[0] * n for _ in range(n)]

   for chain_len in range(2, n + 1):
       for i in range(n - chain_len + 1):
           j = i + chain_len - 1
           m[i][j] = float('inf')
           for k in range(i, j):
               cost = m[i][k] + m[k + 1][j] + p[i] * p[k + 1] * p[j + 1]
               if cost < m[i][j]:
                   m[i][j] = cost
                   s[i][j] = k
   return m, s

def print_optimal_parens(s, i, j):
   if i == j:
       return f"A{i+1}"
   else:
       left = print_optimal_parens(s, i, s[i][j])
       right = print_optimal_parens(s, s[i][j] + 1, j)
       return f"({left} x {right})"

def main():
   n = int(input("Enter the number of matrices: "))
   dims = []

   for i in range(n):
       r = int(input(f"Enter number of rows for matrix A{i+1}: "))
       c = int(input(f"Enter number of columns for matrix A{i+1}: "))
       if i == 0:
           dims.append(r)
       dims.append(c)

   m, s = matrix_chain_order(dims)
   print("\nMinimum number of multiplications required:", m[0][n - 1])
   print("Optimal parenthesization:", print_optimal_parens(s, 0, n - 1))

if __name__ == "__main__":
   main()
          ''')

def pk_8():
    print(Fore.RED + '''

#Rabin-Karp Algorithm

def rabin_karp_search_all_occurrences(text, pattern):
   pattern_length = len(pattern)
   text_length = len(text)

   def simple_hash(s):
       return sum(ord(c) for c in s)

   pattern_hash = simple_hash(pattern)
   print(f"\nPattern: '{pattern}'")
   print(f"Pattern Length: {pattern_length}")
   print(f"Pattern Hash (sum of ASCII values): {pattern_hash}\n")
   found_indices = []
   for start_index in range(text_length - pattern_length + 1):
       current_substring = text[start_index:start_index + pattern_length]
       current_hash = simple_hash(current_substring)
       print(f"Checking substring '{current_substring}' starting at index {start_index}:")
       print(f" Substring Hash: {current_hash}")
       if current_hash == pattern_hash:
           print(" Hash matches pattern hash. Verifying substring characters...")
           if current_substring == pattern:
               print(f" Pattern found at index {start_index}!\n")
               found_indices.append(start_index)
           else:
               print(" Hash collision! Substring does not match pattern.\n")
       else:
           print(" Hash does not match. Moving to next substring.\n")

   if found_indices:
       print(f"Pattern found at indices: {found_indices}\n")
   else:
       print("Pattern not found in the text.\n")

   return found_indices

input_text = input("Enter the text: ")
input_pattern = input("Enter the pattern to search: ")
rabin_karp_search_all_occurrences(input_text, input_pattern)
         
         

#KMP Algorithm

def boyer_moore_search_all(text, pattern):
   text_length = len(text)
   pattern_length = len(pattern)
   match_indices = []
  
   bad_character_table = {}
   for i in range(pattern_length):
       bad_character_table[pattern[i]] = i
   print("Bad character table:", bad_character_table)
  
   shift_in_text = 0
   while shift_in_text <= text_length - pattern_length:
       index_in_pattern = pattern_length - 1
       print(f"\nAttempting pattern alignment at text index: {shift_in_text}")
      
       while index_in_pattern >= 0 and pattern[index_in_pattern] == text[shift_in_text + index_in_pattern]:
           print(f"Matched pattern[{index_in_pattern}] = '{pattern[index_in_pattern]}' with text[{shift_in_text + index_in_pattern}] = '{text[shift_in_text + index_in_pattern]}'")
           index_in_pattern -= 1
          
       if index_in_pattern < 0:
           print(f"Pattern found at index {shift_in_text} in text.")
           match_indices.append(shift_in_text)
          
           next_index = shift_in_text + pattern_length
           if next_index < text_length:
               next_char = text[next_index]
               shift_amount = pattern_length - bad_character_table.get(next_char, -1)
           else:
               shift_amount = 1
           shift_in_text += shift_amount
       else:
           mismatched_char = text[shift_in_text + index_in_pattern]
           last_occurrence_index = bad_character_table.get(mismatched_char, -1)
           shift_amount = max(1, index_in_pattern - last_occurrence_index)
           print(f"Mismatch at pattern[{index_in_pattern}] = '{pattern[index_in_pattern]}' and "
                 f"text[{shift_in_text + index_in_pattern}] = '{mismatched_char}'")
           print(f"Shifting pattern to the right by {shift_amount} positions")
           shift_in_text += shift_amount
          
   if not match_indices:
       print("Pattern not found in text.")
   return match_indices

input_text = input("Enter the text: ")
input_pattern = input("Enter the pattern to search for: ")
matches = boyer_moore_search_all(input_text, input_pattern)
if matches:
   print(f"\nPattern found at indices: {matches}")
else:
   print("\nPattern not found.")

          ''')
    
def pk_9():
    print(Fore.RED + '''
          
#Activity Selection

def activity_selection(start, finish):
   # Number of activities
   n = len(start)
   # Step 1: Sort activities by finish time
   activities = sorted(zip(start, finish, range(1, n+1)), key=lambda x: x[1])
   # Print sorted activities
   print("\nSorted activities by finish time (Activity, Start, Finish):")
   for activity in activities:
       print(f"A{activity[2]}: Start: {activity[0]}, Finish: {activity[1]}")
   # Store the first selected activity
   selected_activities = []
   last_finish_time = -1 # Initially, no activity has been selected
   print("\nActivity Selection Process:")
   # Step 2: Iterate through sorted activities and select the ones that don't overlap
   for activity in activities:
       # If the start time of the current activity is >= finish time of last selected
       if activity[0] >= last_finish_time:
           selected_activities.append(activity)
           last_finish_time = activity[1]
           print(f"Selected activity: A{activity[2]}: Start: {activity[0]}, Finish: {activity[1]}")
   # Final selected activities
   print("\nFinal selected activities:")
   for activity in selected_activities:
       print(f"A{activity[2]}: Start: {activity[0]}, Finish: {activity[1]}")
   # Print the total number of selected activities
   print(f"\nTotal number of activities that can be selected: {len(selected_activities)}")

# Function to take user input for start and finish times as space-separated values
def get_user_input():
   start_times = list(map(int, input("Enter space-separated start times: ").split()))
   finish_times = list(map(int, input("Enter space-separated finish times: ").split()))
  
   return start_times, finish_times

# Main function to run the program
def main():
   start_times, finish_times = get_user_input()
   activity_selection(start_times, finish_times)

# Run the program
if __name__ == "__main__":
   main()


#Huffman Coding

import heapq
from collections import defaultdict
# Step 1: Build the frequency dictionary from the input string
def build_frequency_dict(text):
   freq = defaultdict(int)
   for char in text:
       freq[char] += 1
   return freq

# Step 2: Build the Huffman Tree (using a priority queue/heap)
def build_huffman_tree(freq):
   # Create a priority queue (min-heap) of nodes based on frequency
   heap = [[weight, [char, ""]] for char, weight in freq.items()]
   heapq.heapify(heap)
   # While there is more than one node in the heap
   while len(heap) > 1:
       lo = heapq.heappop(heap) # Get two nodes with lowest frequencies
       hi = heapq.heappop(heap)
      
       # Create a new node with combined frequency
       for pair in lo[1:]:
           pair[1] = '0' + pair[1] # Assign 0 to the left branch
       for pair in hi[1:]:
           pair[1] = '1' + pair[1] # Assign 1 to the right branch
       # Push the merged node back into the heap
       heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
   # Return the final tree (root node)
   return heap[0]

# Step 3: Generate the Huffman codes from the tree
def huffman_codes(tree):
   return {char: code for char, code in tree[1:]}

# Step 4: Encode the input text
def encode(text, codes):
   return ''.join(codes[char] for char in text)

# Step 5: Decode the encoded text
def decode(encoded_text, codes):
   reversed_codes = {v: k for k, v in codes.items()}
   current_code = ""
   decoded_text = ""
  
   for bit in encoded_text:
       current_code += bit
       if current_code in reversed_codes:
           decoded_text += reversed_codes[current_code]
           current_code = ""
  
   return decoded_text

# Step 6: Calculate space saved
def calculate_space_saved(text, encoded_text, freq_dict, codes):
   # Original size in bits (each character is 8 bits)
   original_size = len(text) * 8
  
   # Encoded size in bits (sum of the lengths of the Huffman codes for each character)
   encoded_size = sum(len(codes[char]) * freq_dict[char] for char in freq_dict)
  
   # Calculate space saved
   space_saved = original_size - encoded_size
   space_saved_percentage = (space_saved / original_size) * 100  
   return original_size, encoded_size, space_saved, space_saved_percentage

# Main function to tie everything together
def huffman_coding(text):
   # Build the frequency dictionary
   freq_dict = build_frequency_dict(text)
  
   # Build the Huffman tree
   huffman_tree = build_huffman_tree(freq_dict)
  
   # Generate Huffman codes
   codes = huffman_codes(huffman_tree)
  
   # Encode the input text
   encoded_text = encode(text, codes)
  
   # Decode the encoded text
   decoded_text = decode(encoded_text, codes)

   # Calculate space saved
   original_size, encoded_size, space_saved, space_saved_percentage = calculate_space_saved(text, encoded_text, freq_dict, codes)

   # Print Frequency Dictionary in a readable format
   print(f"--- Frequency Dictionary ---")
   for char, freq in freq_dict.items():
       print(f"Character: '{char}' | Frequency: {freq}")

   # Print Huffman Codes in a readable format
   print("\n--- Huffman Codes ---")
   for char, code in codes.items():
       print(f"Character: '{char}' | Huffman Code: {code}")
  
   # Print Encoded and Decoded Text
   print(f"\n--- Encoded Text ---\n{encoded_text}")
   print(f"\n--- Decoded Text ---\n{decoded_text}")

   # Print Space Comparison
   print(f"\n--- Space Comparison ---")
   print(f"Original size: {original_size} bits")
   print(f"Encoded size: {encoded_size} bits")
   print(f"Space saved: {space_saved} bits")
   print(f"Space saved percentage: {space_saved_percentage:.2f}%")
  
# Input: a string
if __name__ == "__main__":
   input_text = input("Enter the string to encode: ")
   print()
   huffman_coding(input_text)

          
          ''')
    
def pk_10():
    print(Fore.RED + '''
          
#Vertex Cover Problem

from collections import Counter

def vertex_cover(edges):
   
   cover = set()
   edges = list(edges)
   
   while edges:
       # Count degree of each vertex
       degree = Counter()
       for u, v in edges:
           degree[u] += 1
           degree[v] += 1
       
       # Pick vertex with highest degree
       vertex = max(degree, key=degree.get)
       cover.add(vertex)
       
       # Remove all edges containing this vertex
       edges = [(u, v) for u, v in edges if vertex != u and vertex != v]
   
   return cover

# Input: number of edges and the edges
def main():
   n = int(input("Number of edges: "))
   edges = []
   print("Enter edges (u v):")
   for _ in range(n):
       u, v = map(int, input().split())
       edges.append((u, v))
  
   cover = vertex_cover(edges)
   print("Vertex Cover:", cover)

if __name__ == "__main__":
   main()




#TSP

def tsp_nearest_neighbor(dist_matrix, start):
   n = len(dist_matrix)
   visited = [False] * n
   path = [start]
   visited[start] = True
   total_dist = 0
  
   for _ in range(n - 1):
       last = path[-1]
       next_city = None
       min_dist = float('inf')
      
       for city in range(n):
           if not visited[city] and dist_matrix[last][city] < min_dist:
               min_dist = dist_matrix[last][city]
               next_city = city
              
       path.append(next_city)
       visited[next_city] = True
       total_dist += min_dist
  
   # return to start
   total_dist += dist_matrix[path[-1]][start]
   path.append(start)  
   return path, total_dist

def main():
   n = int(input("Enter number of cities: "))
   print("Enter the distance matrix (each row in a new line, distances separated by space):")
  
   dist_matrix = []
   for _ in range(n):
       row = list(map(float, input().split()))
       dist_matrix.append(row)
  
   start = int(input(f"Enter starting city (0 to {n-1}): "))
   if not (0 <= start < n):
       print("Invalid starting city!")
       return
  
   path, dist = tsp_nearest_neighbor(dist_matrix, start)
   print("Path taken:", " -> ".join(map(str, path)))
   print(f"Total distance: {dist:.2f}")

if __name__ == "__main__":
   main()



#Subset Sum Problem

def subset_sum(nums, target):
   n = len(nums)
   dp = [[False] * (target + 1) for _ in range(n + 1)]
  
   for i in range(n + 1):
       dp[i][0] = True
      
   for i in range(1, n + 1):
       for j in range(1, target + 1):
           if nums[i-1] > j:
               dp[i][j] = dp[i-1][j]
           else:
               dp[i][j] = dp[i-1][j] or dp[i-1][j - nums[i-1]]
              
   if not dp[n][target]:
       return False, []
      
   # Backtrack to find the subset
   subset = []
   i, j = n, target
   while i > 0 and j > 0:
       # If the value comes from the top (without current element)
       if dp[i-1][j]:
           i -= 1
       else:
           # Current element is included
           subset.append(nums[i-1])
           j -= nums[i-1]
           i -= 1
          
   return True, subset[::-1] # Reverse to maintain original order

# Taking input from user
nums = list(map(int, input("Enter numbers separated by spaces: ").split()))

target = int(input("Enter the target sum: "))
exists, subset = subset_sum(nums, target)
if exists:
   print("Subset with target sum exists:", subset)
else:
   print("No subset with the target sum exists.")

          ''')