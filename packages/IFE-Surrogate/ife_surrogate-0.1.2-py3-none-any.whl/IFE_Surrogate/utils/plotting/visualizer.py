import matplotlib.pyplot as plt
from jaxtyping import Array
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import matplotlib as mpl
import h5py as h5
from collections.abc import Iterable
from IFE_Surrogate.utils.metrics import nrms, rmse

class Visualizer:
    """
    Container class for useful plotting functions.
    Can also export figures to a PDF-File.
    """


    def save_to_page(self,
                     figures, 
                     file_name: str = "output.pdf"):
        """Function to export matplotlib figures to PDF

        Args:
            figures (iterable[matplotlib.pyplot.figure]): List of matplotlib figures, each 
                                                          figure adds anew page to the output PDF
                                                          Also allows single figure.
            file_name (str, optional): Path and name of the PDF
                                       Defaults to "output.pdf".
        """
        try:
            iter(figures)
            
            with PdfPages(file_name) as pdf:
                for figure in figures:
                    pdf.savefig(figure)
                    plt.close()
        except TypeError:
            with PdfPages(file_name) as pdf:
                pdf.savefig(figures)
                plt.close()


    def plot_bounded_error(self, x, y, error,
                           function_color="blue",
                           error_color="lightblue", 
                           highlight_threshold=0, 
                           highlight_color="red"):
        """Default bounded error plot.

        Args:
            x (_type_): _description_
            y (_type_): _description_
            error (_type_): _description_

        Returns:
            matplotlib.pyplot.figure: figure can be adjusted afterwards.
        """
        fig, ax = plt.subplots()

        ax.plot(x, y, color=function_color, label="Function", linewidth=1)
        sns.set_theme(style="white")

        ax.fill_between(x, y - error, y + error, label="Error Bounds", color=error_color, alpha=0.75)

        if highlight_threshold != 0:
            ax.fill_between(x,
                            y - error,
                            y + error,
                            label="Error Bounds", color=highlight_color, where=np.array([True if i > highlight_threshold else False for i in error]), alpha=0.75)
        
        ax.set_title("Title", fontsize=14)
        ax.set_xlabel("X-Axis", fontsize=12)
        ax.set_ylabel("Y-Axis", fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.5)
        return fig
    

    def plot_sns(self):
        fig, ax = plt.subplots()
        sns.set_theme(style="darkgrid")
        fmri = sns.load_dataset("fmri")

        # Plot the responses for different events and regions
        sns.lineplot(x="timepoint", y="signal",
             hue="region", style="event",
             data=fmri, ax=ax)
        
        return fig


    def plot_testset(
            self,
            frequency: Array, 
            test_y: Array, 
            prediction: Array, 
            var_pred: Array = None, 
            grid: tuple = (4, 4),
            figsize: tuple = (15, 15),
            log_scale: bool = True,
            error: str = "nrms"
        )-> plt.figure:
        """
        Plot predicted vs true curves for a test set.

        Each subplot shows the true and predicted frequency response for one test sample.
        If predictive variance is given, 95% confidence intervals (±2 std) are shown.

        Args:
            frequency (Array): 1D array of frequency values of shape (p,).
            test_y (Array): True output values of shape (n_test, p).
            prediction (Array): Predicted output values of shape (n_test, p).
            var_pred (Array, optional): Predictive variances of shape (n_test, p).
                                        If provided, uncertainty bands are shown.
            grid (tuple): Grid size as (rows, cols) to arrange the subplots.
            figsize (tuple): Size of the overall figure.
            log_scale (bool): If True, x-axis is displayed in logarithmic scale.
            error (str): Type of error metric to show in the title of each plot.
                        Currently only supports "rmse" and "nrms.

        Returns:
            matplotlib.figure.Figure: The generated matplotlib figure.
        """
        fig, ax  = plt.subplots(grid[0], grid[1], figsize=figsize)
        
        if grid[0] == 1 and grid[1] == 1:
            ax = np.array([ax])
        else:
            ax = ax.flatten()

        for i in range(grid[0]*grid[1]):
            ax[i].plot(frequency, test_y[i, :], color='black')
            ax[i].plot(frequency, prediction[i, :], color='blue')
            if var_pred is not None:
                pred_std = np.sqrt(var_pred[i, :])
                ax[i].fill_between(
                    frequency, 
                    prediction[i, :] - 2*pred_std, 
                    prediction[i, :] + 2*pred_std, 
                    color='blue', alpha=0.2
                )
        
            ax[i].set_ylabel('dB')
            ax[i].legend(['True', 'Predicted'])
            #ax[i].grid()
            if log_scale:
                ax[i].set_xscale('log')
            if error == "rmse":
                test_error = rmse(test_y[i, :], prediction[i, :]).item() * 100
            elif error == "nrms":
                test_error = nrms(test_y[i, :], prediction[i, :]).item() * 100
            ax[i].set_title(f'Index: {i}, {error}: {test_error:.3f} %')
            #add axis only for the last row
            if i >= grid[0]*(grid[1]-1):
                ax[i].set_xlabel('Frequency (Hz)')
            plt.tight_layout()
        return fig




    @staticmethod
    def quickplot(data_dict: dict, fig_height=2, fig_width=7):
        for key in data_dict.keys():
            ## Assume the axis with most entries is x-axis
            # print("length of ", len(data_dict[key].shape))
            data = np.array(data_dict[key])
            if data.ndim == 1:
                data = data.reshape(-1, 1)
            nr_plots = min(data.shape)
            xaxis = np.argmax(data.shape)
            yaxis = np.argmin(data.shape)
            # print("selectes axis: ", xaxis)

            # print(slices)
            proceed = input(f"Plot {nr_plots} plots for key '{key}'? (y/n)")
            if proceed == "y":
                fig, ax = plt.subplots(nr_plots, 1)
                if not isinstance(ax, Iterable):
                    ax = [ax]

                fig.set_figheight(fig_height*nr_plots)
                fig.set_figwidth(fig_width)

                
                # indices = [i for i in range(dt.shape[xaxis])]
                moved = np.moveaxis(data, yaxis, 0)
                print(moved.shape)
                for i in range(nr_plots):
                    
                    ax[i].scatter([i for i in range(len(moved[i]))], moved[i], color="k", marker="x", s=1)
                    ax[i].title.set_text(f"{key}: {i}")
                    # ax[i].scatter([i for i in range(dt.shape[xaxis])], dt[tuple(slices)])
                plt.show()
            else:
                print("Aborted.")
                



if __name__ == "__main__":
    

    dummy_data = {
                    "X": np.random.randint(0, 10, size=(100, 2)),
                    "Y": np.random.randint(0, 10,size=(10, 2)),
                    "f": np.random.randint(0, 10, size=(100, 2))
    }

    Visualizer.quickplot(dummy_data)

    # fig1, ax1 = plt.subplots(3, 3)
    # ax1 = ax1[0][0]
    # ax1.plot([1, 2, 3], [1, 4, 9])
    # ax1.set_title('Sample Plot 1')

    # fig2, ax2 = plt.subplots()
    # ax2.plot([1, 2, 3], [9, 4, 1])
    # ax2.set_title('Sample Plot 2')

    # figs = [fig1, fig2]


    # x = np.array([x for x in range(7)])
    # y = np.array([3, 9, 5, 9, 2, 8, 9])
    # err = np.array([np.random.randn() for _ in range(7)])
    # # print(x, y-err, y+err)

    # # plt.plot(x, y, label="Main Function")

    # # plt.fill_between(x, y - err, y + err, label="Error Bounds")
    # # plt.show()
    # v = Visualizer()
    # figs.append(v.plot_bounded_error(x, y, err, highlight_threshold=2))

    # print(figs)
    # v.save_to_page(figs)

