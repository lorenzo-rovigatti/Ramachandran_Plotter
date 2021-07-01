''' ================================================================================================================

	Functions here are called by main() to plot data generated by main(). A background plot of favourable dihedral 
	angles (as determined by the Top8000 data set of peptide structures solved at high resolutions) is generated. 
	Then contour lines and the dihedral angles from the user's PDB file are plotted on top, before formatting is 
	applied. 
	
	Version 2.0.1:
	 - Relies on the easily accessible Biopython package, rather than Phenix as in versions <2.0
	 - User arguments can be now easily parsed in from the command line
	 - If required, the script could be implemented into existing protein analysis pipelines by importing this 
	 function ( main() )

	Author information:
	 - Joseph I. J. Ellaway
	 - josephellaway@gmail.com
	 - https://github.com/Joseph-Ellaway

	================================================================================================================ '''


from scipy import ndimage
import cv2
import os
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.colors import LogNorm

# LaTeX functionality
import matplotlib
matplotlib.rcParams['text.usetex'] = True		# Enable LaTeX in annotations. 
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{siunitx} \sisetup{detect-all} \usepackage{helvet} \usepackage{sansmath} \sansmath' # Sans-serif math

# Removes qt5ct messages. Comment out to debug
os.environ['QT_LOGGING_RULES']="qt5ct.debug=false"

# Change to suit taste

def AxesRemover(mpl_axis):
	'''
	=========================================================
	Removes axes and tick marks from a given Matplotlib axis. 
	=========================================================
	'''
	mpl_axis.set_frame_on(False)
	mpl_axis.get_xmpl_axis().tick_bottom()
	mpl_axis.get_ympl_axis().set_visible(False)
	mpl_axis.get_xmpl_axis().set_visible(False)



def SaveAndCloseFigure(out_file_name, resolution):			# dtypes : string, int 
	'''
	=======================================================================================================
	Saves the plot area (defined before function called) as a PNG image to given file name and resolution. 
	=======================================================================================================
	'''
	plt.savefig(out_file_name, dpi=resolution, bbox_inches=0, pad_inches=None)
	plt.close()



def PhiPsiPlotter(phi_angles, psi_angles, figsize, file_name, background_colour):	# dtypes : array-like, 
	'''
	=====================================================================================================
	Creates a 2D histogram (Ramachandran plot) of out of phi and psi angles from the Top8000 peptide DB.
	=====================================================================================================
	'''
	fig, ax = plt.subplots(1,1, figsize=figsize, tight_layout=True)
	fig.patch.set_visible(False)
	kwargs = {
		'bins' : 140, 
		'cmap' : background_colour, 
		'norm' : colors.PowerNorm(0.1),
		'alpha' : 1}
	# Reference https://matplotlib.org/3.2.1/gallery/statistics/hist.html for help with making 2D histogram.
	ax.set_axis_off()
	ax.hist2d(phi_angles, psi_angles, **kwargs)
	SaveAndCloseFigure(file_name, 80)



def Smoother(file_name, figsize, background_colour):
	'''
	==========================================================================================================================================
	Reads a given pixelated image (passed into function as the file name as a string) and 'smoothes' it out to create an unpixelated version.
	The unpixelated ('smoothed') version is then saved to ~/your_current_dir, overwriting the pixelated input image. 
	==========================================================================================================================================
	'''
	fig, ax = plt.subplots(1,1, figsize=figsize, tight_layout=True)
	fig.patch.set_visible(False)
	kwargs = {
		'cmap' : str(background_colour + '_r'), 
		'alpha' : 1}
	ax.set_axis_off()
	rama_plot = cv2.imread(file_name, 0)
	blurred_rama_plot = ndimage.gaussian_filter(rama_plot, sigma=0.3)
	smoothed_rama_plot = ndimage.percentile_filter(blurred_rama_plot, percentile=90, size=20)
	ax.imshow(smoothed_rama_plot, **kwargs)
	bkgd_resolution = 96									# Adjust integer to change background resolution (higher = better quality but slower run time)
	SaveAndCloseFigure(file_name, bkgd_resolution)
	plt.close()



def MakeBackground(dihedral_df, plot_type, file_name, background_colour):
	'''
	==========================================================================================================================================
	Reads a given pixelated image (passed into function as the file name as a string) and 'smoothes' it out to create an unpixelated version.
	The unpixelated ('smoothed') version is then saved to ~/your_current_dir, overwriting the pixelated input image. 
	==========================================================================================================================================
	'''
	# Uses Top8000 DB
	figure_size_background=(10,10)								# Does not change output image size. 

	if plot_type == 'All':
		pass

	elif plot_type == 'Proline':
		dihedral_df = dihedral_df.loc[(dihedral_df['type'] == 'Trans-proline') | dihedral_df['type'] == 'Cis-proline']

	else:
		dihedral_df = dihedral_df.loc[dihedral_df['type'] == plot_type]

	file_name = str(file_name + '.png')

	PhiPsiPlotter(dihedral_df['phi'], dihedral_df['psi'], figure_size_background, file_name, background_colour)

	Smoother(file_name, figure_size_background, background_colour)



def AddContour(axis, df, contour_level, line_colour, contour_alpha=1):
	'''
	===============================================================
	Appends contour lines to a given axis based on phi/psi angles. 
	===============================================================
	'''

	counts, discard1, discard2, discard3 = plt.hist2d(df['phi'],df['psi'], bins=90, norm=LogNorm(), alpha=0)
	axis.contour(counts.transpose(), extent=[-180, 180, -180, 180], levels=[contour_level], linewidths=1, colors=[line_colour], zorder=2, alpha=contour_alpha)



def AddGridLines(axis):
	'''
	==============================
	Appends grid lines to an axis. 
	==============================
	'''

	# AESTHETIC CHOICES
	zero_lines_kwargs = {
		'colors' : ['Grey'], 
		'alpha' : 0.4, 
		'zorder' : 3, 
		'linewidths' : [1]
		}

	axis.grid(alpha=0.4, linestyle='--', linewidth=1, color='Grey', zorder=3)
	axis.hlines(0, -180, 180, **zero_lines_kwargs)
	axis.vlines(0, -180, 180, **zero_lines_kwargs)


def FormatAxis(axis):
	'''
	=========================================
	Adds aesthetic features to a given axis. 
	=========================================
	'''

	axis.set_xlim((-180, 180))
	axis.set_ylim((-180, 180))
	axis.set_xlabel(r'$\phi \ (\si{\degree})$')
	axis.set_ylabel(r'$\psi \ (\si{\degree})$')
	ax_linewidth = 2
	axis.spines['left'].set_linewidth(ax_linewidth)
	axis.spines['bottom'].set_linewidth(ax_linewidth)