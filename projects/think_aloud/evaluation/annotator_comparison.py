import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

# Loading the data
total_df = pd.DataFrame()
for file in os.listdir('all_annotations_data'):
    name = file.split('_')[-1].split('.')[0].capitalize()
    df = pd.read_csv('all_annotations_data/'+file)
    df = df[['engaging','specific','relevant','correct','semantically appropriate']]
    df['average score'] = df.mean(axis=1)
    df['name'] = name
    total_df = total_df.append([df], ignore_index = True)

# Plotting data per category, comparing annotators
categories = total_df.columns.drop('name')
fig, axes = plt.subplots(1, 6)
sns.set(font_scale=0.5)
for category, ax in zip(categories, axes.flatten()):
    plt.xticks(rotation=90)
    sns.boxplot(y = category, x="name", data=total_df, orient='v', ax=ax).set(
    xlabel= '')
    # sns.histplot(x="name", data=total_df, y=category, ax=ax).set(
    # xlabel= '')
    # sns.barplot(x="name", data=total_df, y=category, ax=ax).set(
    # xlabel= '')
plt.tight_layout()
for ax in fig.axes:
    ax.tick_params(labelrotation=45)
plt.show()


# Test between annotators per category
for category in ['engaging','specific','relevant','correct','semantically appropriate','average score']:
    print('Category ', category)

    # ANOVA (NOT NEEDED AFTER ALL)
    fvalue, pvalue = stats.f_oneway(total_df.loc[total_df['name'] == 'Thomas'][category],
                                    total_df.loc[total_df['name'] == 'Fina'][category],
                                    total_df.loc[total_df['name'] == 'Imme'][category])
    print('Mean values')
    print('Thomas', total_df.loc[total_df['name'] == 'Thomas'][category].mean().round(2),
    'Fina', total_df.loc[total_df['name'] == 'Fina'][category].mean().round(2),
    'Imme', total_df.loc[total_df['name'] == 'Imme'][category].mean().round(2),
    'Category mean', total_df[category].mean().round(2))
    print('F-value', fvalue.round(3),'p-value', pvalue.round(3))

    # Levene’s test for homogeneity of variance
    print('Levene’s test for homogeneity of variance')
    print(stats.levene(total_df.loc[total_df['name'] == 'Thomas'][category],
                 total_df.loc[total_df['name'] == 'Fina'][category],
                 total_df.loc[total_df['name'] == 'Imme'][category]))

    # Kolmogorov-Smirnov test
    print('Kolmogorov-Smirnov test')
    print(stats.kstest(total_df.loc[total_df['name'] == 'Thomas'][category], 'norm'))
    print(stats.kstest(total_df.loc[total_df['name'] == 'Fina'][category] , 'norm'))
    print(stats.kstest(total_df.loc[total_df['name'] == 'Imme'][category], 'norm' ))

    # Kruskal-Wallis H-test for independent samples
    statistic, pvalueWallis = stats.kruskal(total_df.loc[total_df['name'] == 'Thomas'][category],
                                    total_df.loc[total_df['name'] == 'Fina'][category],
                                    total_df.loc[total_df['name'] == 'Imme'][category])
    print('Kruskal-Wallis test: ', statistic, pvalueWallis,'\n')

