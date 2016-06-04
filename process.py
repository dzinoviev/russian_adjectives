import pandas as pd
import matplotlib, matplotlib.pyplot as plt
import toposort, itertools

matplotlib.rc("font", family="Arial") 
matplotlib.style.use('ggplot')

scores = pd.read_csv("Adjectives_on_a_scale.csv", 
                   header=1).set_index('ResponseID')#.fillna(0)
print("Scores:", len(scores), "rows")
ranks = pd.read_csv("Adjectives.csv", 
                    header=1).set_index('ResponseID').fillna(0)
print("Ranks:", len(ranks), "rows")
ranks_improved = pd.read_csv("Adjectives_Improved.csv", 
                    header=1).set_index('ResponseID').fillna(0)
print("Ranks (improved):", len(ranks_improved), "rows")

print("Unique subjects:", len(pd.concat([scores['IPAddress'],
                                         ranks['IPAddress'],
                                         ranks_improved['IPAddress']]).unique()))

scores.columns = scores.columns.str.replace(r'Оцените качество каждого водителя по шкале от самого плохого \(0\) до самого хорошего \(100\)....-', '')
scores.columns = scores.columns.str.replace(' водитель', '')
ranks.columns = ranks.columns.str.replace(r'Расположите слова по порядку от обозначающего самое положительное качество наверху до обозначающе...-','')
ranks_improved.columns = ranks_improved.columns.str.replace(r'Расположите слова по порядку от обозначающего минимально отрицательное качество наверху до обо...-','')
ranks_improved.columns = ranks_improved.columns.str.replace(r'Расположите слова по порядку от обозначающего максимально положительное качество наверху до об...-','')
ranks_improved.columns = ranks_improved.columns.str.replace(r'Расположите слова по порядку от обозначающего самое положительное качество наверху до обознача...-','')

scores = scores.ix[:, 9:-4]
ranks = ranks.ix[:, 9:-4]
ranks_improved = ranks_improved.ix[:, 9:-4]
scores_median = scores.median()
terciles = pd.qcut(scores_median, 3)
bottom_tercile = terciles.values.categories[0]
top_tercile = terciles.values.categories[-1]

ranks1 = ranks[
    ranks[scores_median[terciles == top_tercile].index].max(axis=1)
    <= ranks[scores_median[terciles == bottom_tercile].index].min(axis=1)]
print("Ranks (cleaned):", len(ranks1), "rows")

print("Not used in the improved set:", 
      set(ranks.columns) - set(x[3:] for x in ranks_improved.columns))

def ranks2order(ranks, majority = False):
    big = pd.DataFrame([[(ranks[j] > ranks[i]).sum() 
                         for i in ranks.columns] 
                        for j in ranks.columns])
    big.columns = ranks.columns
    big.index = ranks.columns
    if not majority:
        majority = big.max().max()
    graph = sorted(big[big >= majority].stack().index.tolist())
    big_dict = dict([(x, set(a[1] for a in y)) for (x, y) 
                     in itertools.groupby(graph, key=lambda x: x[0])])
    true_order = list(toposort.toposort(big_dict))
    print("Majority:", majority / len(ranks))
    return true_order

print("Toposort by ranks")
true_order = ranks2order(ranks1, 121)
print([scores[list(grp)].mean().sort_values(ascending=False).index.tolist() 
       for grp in true_order])

print("Toposort by score ranks")
score_ranks = scores.rank(axis=1)
true_order = ranks2order(score_ranks, 54)
print([scores[list(grp)].mean().sort_values(ascending=False).index.tolist() 
       for grp in reversed(true_order)])

print("Toposort by ranks in groups")
for prefix,limit in (("1", 130), ("2", 127), ("3", 115)):
    r = ranks_improved[[x for x in ranks_improved.columns 
                        if x.startswith(prefix)]]
    true_order = ranks2order(r, limit)
    print([scores[[x[3:] for x in grp]].mean().sort_values(ascending=False).index.tolist() 
           for grp in true_order])
    
order = scores_median.sort_values().index
scores[order].plot(kind='box', vert=False)
plt.title('Оценки прилагательных упорядочены по медиане')
plt.tight_layout()
#plt.show()
plt.savefig("scores.png", dpi=150)

fig = plt.figure() 
ax = fig.add_subplot(111)
cs = ax.matshow(scores[order].corr())
ax.set_yticks(range(len(scores.columns)))
ax.set_yticklabels(order)
plt.title('Корреляции оценок')
plt.tight_layout()
#plt.show()
plt.savefig("scores-corr.png", dpi=150)

order = ranks1.median().sort_values(ascending=False).index
ranks1[order].plot(kind='box', vert=False)
plt.title('Позиции прилагательных упорядочены по медиане')
plt.tight_layout()
#plt.show()
plt.savefig("ranks.png", dpi=150)

fig = plt.figure() 
ax = fig.add_subplot(111)
cs = ax.matshow(ranks1[order].corr())
ax.set_yticks(range(len(ranks1.columns)))
ax.set_yticklabels(order)
plt.title('Корреляции позиций')
plt.tight_layout()
#plt.show()
plt.savefig("ranks-corr.png", dpi=150)
