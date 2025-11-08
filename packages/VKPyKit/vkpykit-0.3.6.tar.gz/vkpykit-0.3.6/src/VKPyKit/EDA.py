import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score, confusion_matrix
from IPython.display import display
# To ignore unnecessary warnings
import warnings
warnings.filterwarnings("ignore")   

class EDA:

    def __init__(self):
        pass

    RANDOM_STATE = 42
    NUMBER_OF_DASHES = 100

    """
    To plot simple EDA visualizations
    """
    # function to plot stacked bar chart
    def barplot_stacked(self, 
                        data : pd.DataFrame, 
                        predictor: str , 
                        target: str) -> None:
        """
        Print the category counts and plot a stacked bar chart
        data: dataframe \n
        predictor: independent variable \n
        target: target variable \n
        return: None
        """
        count = data[predictor].nunique()
        sorter = data[target].value_counts().index[-1]
        tab1 = pd.crosstab(data[predictor], data[target], margins=True).sort_values(
            by=sorter, ascending=False
        )
        print(tab1)
        print("-" * self.NUMBER_OF_DASHES)
        tab = pd.crosstab(data[predictor], data[target], normalize="index").sort_values(
            by=sorter, ascending=False
        )
        tab.plot(kind="bar", stacked=True, figsize=(count + 5, 6))
        plt.legend(
            loc="lower left", frameon=False,
        )
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.show()

    # function to create labeled barplot
    def barplot_labeled(
            self,
            data: pd.DataFrame, 
            feature: str, 
            percentages: bool =False, 
            category_levels : int =None):
        """
        Barplot with percentage at the top

        data: dataframe \n  
        feature: dataframe column \n
        percentages: whether to display percentages instead of count (default is False) \n
        category_levels: displays the top n category levels (default is None, i.e., display all levels) \n
        return: None
        """

        totalfeaturesvalues = len(data[feature])  # length of the column
        count = data[feature].nunique()
        if category_levels is None:
            plt.figure(figsize=(count + 2, 6))
        else:
            plt.figure(figsize=(category_levels + 2, 6))

        plt.xticks(rotation=90, fontsize=15)
        ax = sns.countplot(
            data=data,
            x=feature,
            palette="Paired",
            order=data[feature].value_counts().index[:category_levels] if category_levels else None,
        )

        for p in ax.patches:
            if percentages == True:
                label = "{:.1f}%".format(100 * p.get_height() / totalfeaturesvalues)  # percentage of each class of the category
            else:
                label = p.get_height()  # count of each level of the category

            x = p.get_x() + p.get_width() / 2  # width of the plot
            y = p.get_height()  # height of the plot

            ax.annotate(
                label,
                (x, y),
                ha="center",
                va="center",
                size=12,
                xytext=(0, 5),
                textcoords="offset points",
            )  # annotate the percentage

        plt.show()  # show the plot

    # function to plot a boxplot and a histogram along the same scale.
    def histogram_boxplot(
            self,
            data : pd.DataFrame, 
            feature: str, 
            figsize : tuple[float, float] =(12, 7), 
            kde : bool = False, 
            bins : int = None) -> None:
        """
        Boxplot and histogram combined
        data: dataframe \n
        feature: dataframe column \n
        figsize: size of figure (default (12,7)) \n
        kde: whether to the show 'Kernel Desity Estimate (KDE)' curve (default False) \n
        bins: number of bins for histogram (default None) \n
        return: None
        """
        f2, (ax_box2, ax_hist2) = plt.subplots(
            nrows=2,  # Number of rows of the subplot grid= 2
            sharex=True,  # x-axis will be shared among all subplots
            gridspec_kw={"height_ratios": (0.25, 0.75)},
            figsize=figsize,
        )  # creating the 2 subplots
        sns.boxplot(
            data=data, x=feature, ax=ax_box2, showmeans=True, color="violet"
        )  # boxplot will be created and a star will indicate the mean value of the column
        sns.histplot(
            data=data, x=feature, kde=kde, ax=ax_hist2, bins=bins, palette="winter"
        ) if bins else sns.histplot(
            data=data, x=feature, kde=kde, ax=ax_hist2
        )  # For histogram
        ax_hist2.axvline(
            data[feature].mean(), color="green", linestyle="--"
        )  # Add mean to the histogram
        ax_hist2.axvline(
            data[feature].median(), color="black", linestyle="-"
        )  # Add median to the histogram`

    # function to plot distribution of target variable for different classes of a predictor
    def distribution_plot_for_target(self, 
                                     data : pd.DataFrame, 
                                     predictor : str, 
                                     target : str,
                                     figsize: tuple[float, float]= (12, 10)
                                     ) -> None:

        """
        data: dataframe \n
        predictor: Independent variable \n
        target: Target variable \n
        figsize: size of the figure (default (12,10)) \n
        return: None
        """
        fig, axs = plt.subplots(2, 2, figsize=figsize)

        target_uniq = data[target].unique()

        axs[0, 0].set_title("Distribution of target for target=" + str(target_uniq[0]))
        sns.histplot(
            data=data[data[target] == target_uniq[0]],
            x=predictor,
            kde=True,
            ax=axs[0, 0],
            color="teal",
            stat="density",
        )

        axs[0, 1].set_title("Distribution of target for target=" + str(target_uniq[1]))
        sns.histplot(
            data=data[data[target] == target_uniq[1]],
            x=predictor,
            kde=True,
            ax=axs[0, 1],
            color="orange",
            stat="density",
        )

        axs[1, 0].set_title("Boxplot w.r.t target")
        sns.boxplot(data=data, x=target, y=predictor, ax=axs[1, 0], palette="gist_rainbow")

        axs[1, 1].set_title("Boxplot (without outliers) w.r.t target")
        sns.boxplot(
            data=data,
            x=target,
            y=predictor,
            ax=axs[1, 1],
            showfliers=False,
            palette="gist_rainbow",
        )

        plt.tight_layout()
        plt.show()

    # function to plot boxplots for all numerical features to detect outliers
    def boxplot_outliers(self, 
                         data: pd.DataFrame):
        # outlier detection using boxplot
        """
        data: dataframe \n
        return: None
        """
        features = data.select_dtypes(include=np.number).columns.tolist()

        plt.figure(figsize=(15, 12))

        for i, feature in enumerate(features):
            plt.subplot(1+int(len(features)/3), 3, i + 1) # assign a subplot in the main plot, 3 columns per row
            plt.boxplot(data[feature], whis=1.5)
            plt.tight_layout()
            plt.title(feature)

        plt.show()

    # function to plot a boxplot and a histogram along the same scale.
    def histogram_boxplot_all(
            self,
            data : pd.DataFrame, 
            figsize : tuple[float, float] =(15, 10), 
            bins : int = 10, 
            kde : bool = False) -> None:
        """
        Boxplot and histogram combined
        data: dataframe \n
        feature: dataframe column \n
        figsize: size of figure (default (15,10)) \n
        bins: number of bins for histogram (default : 10) \n
        kde: whether to the display 'Kernel Density Estimate (KDE)' curve (default False) \n
        return: None
        """
        features = data.select_dtypes(include=['number']).columns.tolist()

        plt.figure(figsize=figsize)

        for i, feature in enumerate(features):
            plt.subplot(1+int(len(features)/3), 3, i+1)    # assign a subplot in the main plot, 3 columns per row
            sns.histplot(data=data, x=feature, kde=kde, bins=bins)    # plot the histogram

        plt.figure(figsize=figsize)

        for i, feature in enumerate(features):
            plt.subplot(1+int(len(features)/3), 3, i+1)    # assign a subplot in the main plot
            sns.boxplot(data=data, x=feature)    # plot the histogram

        plt.tight_layout()
        plt.show()
   
    # function to plot heatmap for all numerical features
    def heatmap_all(self, 
                    data : pd.DataFrame,
                    features : list = None
                    ) -> None:
        """
        Plot heatmap for all numerical features\n
        data: dataframe \n
        return: None
        """
        # defining the size of the plot
        plt.figure(figsize=(12, 7))
        if features is None:
            features = data.select_dtypes(include=['number']).columns.tolist()

        # plotting the heatmap for correlation
        sns.heatmap(
            data[features].corr(),annot=True, vmin=-1, vmax=1, fmt=".2f", cmap="Spectral"
        )
    
    # function to plot pairplot for all numerical features
    def pairplot_all(self, 
                    data : pd.DataFrame,
                    features : list[str] = None,
                    hues: list[str] = None,
                    min_unique_values_for_pairplot : int = 4,
                    diagonal_plot_kind: str = "auto"
                    ) -> None:
        """
        Plot heatmap for all numerical features\n
        data: dataframe \n
        features: list of features to plot (default None, i.e., all numerical features) \n
        hues: list of features to use for coloring (default None, i.e., no coloring) \n
        min_unique_values_for_pairplot: minimum number of unique values for a feature to be plotted (default 4) \n
        diagonal_plot_kind: kind of diagonal plot to use. default "auto"|possible: auto, hist, kde, None \n
        return: None
        """
        # defining the size of the plot
        plt.figure(figsize=(12, 7)) 

        if features is None:
            features = [
                    col for col in data.columns 
                    if pd.api.types.is_numeric_dtype(data[col]) and data[col].nunique() > min_unique_values_for_pairplot
                ]
        if hues is None:
            sns.pairplot(data, vars=features, diag_kind=diagonal_plot_kind)
        else:
            for i, hue in enumerate(hues):
                plt.subplot(1+int(len(features)/3), 3, i+1) # assign a subplot in the main plot, 3 columns per row
                #plotting the heatmap for correlation
                print("Hue: " + hue)
                sns.pairplot(data, vars=features, hue=hue, diag_kind=diagonal_plot_kind)
        
        plt.show()
    
    
    # function to plot distribution of target variable for different classes of a predictor
    def distribution_plot_for_target_all(self, 
                                     data : pd.DataFrame, 
                                     predictors : list[str], 
                                     target : str,
                                     figsize: tuple[float, float]= (12, 10)
                                     ) -> None:

        """
        data: dataframe \n
        predictor: List of Independent variables \n
        target: Target variable \n  
        predictor: 
        """
        for pred in predictors:
            print("-" * 100)
            print(f"Distribution plot_for {target} for predictor:{pred} ")
            self.distribution_plot_for_target(data, pred, target, figsize)

    # function to plot stacked bar chart for all predictors
    def barplot_stacked_all(self, 
                        data : pd.DataFrame, 
                        predictors: list[str],
                        target: str
                        ) -> None:

        """
        data: dataframe \n
        predictor: List of Independent variables \n
        target: Target variable \n  
        predictor: 
        """
        for pred in predictors:
            if pred == target:
                continue
            print("-" * self.NUMBER_OF_DASHES)
            print(f"Stacked barplot for {target} for predictor:{pred} ")
            self.barplot_stacked(data, pred, target)