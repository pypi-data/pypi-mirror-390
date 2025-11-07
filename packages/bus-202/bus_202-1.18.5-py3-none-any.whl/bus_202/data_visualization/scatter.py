def scatter(df, y, x, z=None, fit_line=False, dpi=150, figsize=(6, 4)):
    """
    Create a nice scatter plot with optional fit line and correlation coefficient
    
    Parameters:
    df (pandas DataFrame): Input data
    y (str): Column name for y-axis variable (vertical axis in 3D)
    x (str): Column name for x-axis variable
    z (str, optional): Column name for z-axis variable (creates 3D plot)
    fit_line (bool): If True, adds best fit line (2D) or plane (3D)
    dpi (int): Plot resolution
    figsize (tuple): Figure size
    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d import Axes3D
    
    # 2D scatter plot (original functionality)
    if z is None:
        # Calculate correlation coefficient
        corr = df[x].corr(df[y])
        
        # Set style
        sns.set_style("whitegrid")
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        
        # Create scatter plot
        if fit_line:
            # Use seaborn's regplot for scatter + fit line
            sns.regplot(data=df, 
                       x=x, 
                       y=y,
                       scatter_kws={'alpha':0.5},
                       line_kws={'color': 'red'},
                       ci=None)
        else:
            # Use seaborn's scatterplot
            sns.scatterplot(data=df,
                           x=x,
                           y=y,
                           alpha=0.5)
        
        # Customize plot - 2 variable title format
        plt.title(f'{y} and {x}\nCorrelation: {corr:.3f}', pad=15)
        plt.xlabel(x)
        plt.ylabel(y)
        
        # Adjust layout
        plt.tight_layout()
        
    # 3D scatter plot
    else:
        # Create 3D figure with larger size for better visibility
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111, projection='3d')
        
        # Remove NaN values for plotting
        plot_df = df[[x, y, z]].dropna()
        
        # Create 3D scatter plot with color spectrum and edge color
        # In matplotlib 3D: (x-axis, y-axis, z-axis) where z-axis is VERTICAL
        # So to make y variable vertical, it goes in the 3rd position
        scatter = ax.scatter(plot_df[x], plot_df[z], plot_df[y], 
                            c=plot_df[y], cmap='RdYlBu_r', s=50,
                            edgecolor='black', linewidth=0.5,
                            alpha=0.8)
        
        # Add colorbar with more space
        cbar = plt.colorbar(scatter, ax=ax, pad=0.15, shrink=0.8)
        cbar.set_label(y, rotation=270, labelpad=15)
        
        # Add best-fit plane if requested
        if fit_line:
            # Prepare data for plane fitting: y = a*x + b*z + c
            X_data = np.column_stack([plot_df[x], plot_df[z], np.ones(len(plot_df))])
            y_data = plot_df[y].values
            
            # Fit plane using least squares: [a, b, c]
            coeffs, residuals, rank, s = np.linalg.lstsq(X_data, y_data, rcond=None)
            a, b, c = coeffs
            
            # Create mesh grid for the regression plane
            x_surf = np.linspace(plot_df[x].min(), plot_df[x].max(), 20)
            z_surf = np.linspace(plot_df[z].min(), plot_df[z].max(), 20)
            X_mesh, Z_mesh = np.meshgrid(x_surf, z_surf)
            
            # Calculate y values for the plane
            Y_mesh = a * X_mesh + b * Z_mesh + c
            
            # Plot the regression plane with grid lines and semi-transparency
            # Order: (x-axis, y-axis, z-axis) where z-axis is vertical
            surf = ax.plot_surface(X_mesh, Z_mesh, Y_mesh, 
                                   alpha=0.4, cmap='coolwarm',
                                   edgecolor='black', linewidth=0.5,
                                   rstride=1, cstride=1,
                                   antialiased=True)
        
        # 3 variable title format
        title = f'{y}, {x}, and {z}'
        
        # Set axis labels
        # In matplotlib 3D: x is horizontal left-right, y is horizontal front-back, z is VERTICAL
        ax.set_xlabel(x, labelpad=10)      # horizontal axis
        ax.set_ylabel(z, labelpad=10)      # horizontal axis (front-back)
        ax.set_zlabel(y, labelpad=10)      # VERTICAL axis (up-down)
        
        # Move z-axis (vertical) ticks and label to the left to avoid colorbar overlap
        ax.zaxis._axinfo['juggled'] = (1, 2, 0)  # Move z-axis to left side
        
        # Flip axes to go from least to greatest (normal order)
        ax.invert_xaxis()
        ax.invert_yaxis()
        
        # Adjust the viewing angle for better perspective
        ax.view_init(elev=25, azim=135)
        
        # Make the grid lines more visible
        ax.xaxis._axinfo["grid"]['color'] = (0.5, 0.5, 0.5, 0.5)
        ax.yaxis._axinfo["grid"]['color'] = (0.5, 0.5, 0.5, 0.5)
        ax.zaxis._axinfo["grid"]['color'] = (0.5, 0.5, 0.5, 0.5)
        
        # Set title after everything else
        ax.set_title(title, pad=15)
        
        # Adjust layout
        plt.tight_layout()
    
    # Show plot
    plt.show()
