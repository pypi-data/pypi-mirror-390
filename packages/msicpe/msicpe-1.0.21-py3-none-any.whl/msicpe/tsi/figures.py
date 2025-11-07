import numpy as np
from plotly import express as px
# from plotly import subplots as splt
from plotly.subplots import make_subplots
import pandas as pd



def plotHistograms(centers, hist, cumhist, title=None):
    """
    Affiche sur une même figure un histogramme et l'histogramme
    cumulé correspondant.
    
    Parameters
    ----------
    centers : np.ndarray
        Vecteur d'abscisses
    hist : np.ndarray
        Vecteur des valeurs des bins de l'histogramme
    cumhist : np.ndarray
        Vecteur des valeurs de l'histogramme cumulé
    title (optionnel) : str
        Titre de la figure

    Notes
    ------
    Affiche l'histogramme de l'image (axe des ordonnées de gauche) ainsi
    que l'histogramme cumulé (axe des ordonnées de droite).
    """
    
    # create subplot with secondary axis
    yyaxis_fig = make_subplots(specs=[[{"secondary_y": True}]])

    # plot data independently in fig1 and fig2
    fig1 = px.bar(x=centers,  y=hist, title=title)
    fig1.update_traces(marker_color='purple')
    # fig1.update_yaxes(range=(-1,1.1*np.max(hist)))
    
    fig2 = px.line(x=centers,  y=cumhist)
    fig2.update_traces(line_color='#000000')
    
    # change the axis for fig2
    fig2.update_traces(yaxis="y2")
    # fig2.update_yaxes(range=(-1,1.1*np.max(cumhist)))

    # add the figuress to the subplot figure
    yyaxis_fig.add_traces(fig1.data + fig2.data)

    # format subplot figure
    yyaxis_fig.update_layout(title=title, 
                             yaxis =dict(title=dict(text="histogramme",font=dict(color="purple"))), 
                             yaxis2=dict(title=dict(text="histogramme cumulé",font=dict(color="#000000"))),
    )
    
    max_dyn = 2**int(np.ceil(np.log2(np.max(centers))))
    yyaxis_fig.update_xaxes(range=(0,max_dyn))
    yyaxis_fig.update_yaxes(range=[-.04*np.max(hist),1.1*np.max(hist)], secondary_y=False)
    yyaxis_fig.update_yaxes(range=[-.04*np.max(cumhist),1.1*np.max(cumhist)], secondary_y=True)
    
    yyaxis_fig.show()
    
    #return yyaxis_fig



def add_legend(fig,legend):
    """
    Ajoute une légende aux subplots de la figure fig.
    
    Parameters
    ----------
    fig : px.figure
        Figure plotly
    legend : list
        Liste des légende (il doit y avoir autant de str 
        qu'il y a de subplots dans la figure fig)
    """

    item_map={f'{i}':key for i, key in enumerate(legend)}
    fig.for_each_annotation(lambda a: a.update(text=item_map[a.text.split("=")[1]]))