import csv
with open('sample_out.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))
print('Header:', rows[0])
print('Row 1:', rows[1])
print('Row 5:', rows[5])
print('Row 10:', rows[10])
print('Total rows (with header):', len(rows))
scores = [float(r[2]) for r in rows[1:]]
mono = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
print('Scores non-increasing:', mono)
print('Unique scores (4dp):', len(set(f"{s:.4f}" for s in scores)))
print()
print('Top 15 titles:')
for r in rows[1:16]:
    print(f"  Rank {r[1]:3s}  Score {r[2]}  {r[3][:80]}")
