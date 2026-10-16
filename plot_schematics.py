"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)

def durability(out):
    d=Drawing((0,0,8.5,9.7))
    labels=[
        "Authorize full transfer context\nand immutable session key",
        "Persist mask, blinding,\nand signed proposal outbox",
        "Verify signed private openings;\npersist each entitled component",
        "Issue and persist receipt for\na matching durable component",
        "Verify links, two proposals,\nand six receipts; activate once"]
    ys=[8.9,7.05,5.2,3.35,1.5]
    for i,(y,label) in enumerate(zip(ys,labels)):
        d.box(str(i),4.25,y,8.05,1.05,label,size=8.5)
    for i,label in enumerate(("sample once","send / replay","persist before sign","complete certificate")):
        d.edge(str(i),str(i+1),sa="s",sb="n")
        d.text(4.25,(ys[i]+ys[i+1])/2,label,size=8)
        # Labels occupy a white patch, retaining one continuous flow.
        d.labels[-1][0].set_bbox(dict(facecolor="white",edgecolor="none",pad=1))
    d.save(out,"durability-state")

def protocol(out):
    d=Drawing((0,0,17.4,7.1))
    d.text(1.8,6.1,"Certified old generation",size=8.5)
    d.text(14.45,6.1,"New replicated generation",size=8.5)
    for name,y,label in [
        ("o0",5.25,"$P_0$ retires\nstores $z_1,z_2$"),
        ("o1",3.8,"$P_1$ survives\nstores $z_0,z_2$"),
        ("o2",2.35,"$P_2$ survives\nstores $z_0,z_1$")]:
        d.box(name,1.8,y,2.6,.95,label,size=8.5)
    d.box("d2",5.25,4.25,3.35,1.05,
          "$P_1$: sample $\\delta_2$\nsign $D_2=\\mathrm{Com}(\\delta_2;\\tau_2)$",size=8.5)
    d.box("d1",5.25,2.8,3.35,1.05,
          "$P_2$: sample $\\delta_1$\nsign $D_1=\\mathrm{Com}(\\delta_1;\\tau_1)$",size=8.5)
    d.box("eq",9.75,3.5,4.4,1.65,
          "$z'_1=z_1+\\delta_1,\\quad z'_2=z_2+\\delta_2$\n"
          "$z'_0=z_0-\\delta_1-\\delta_2$\nsame equations for blindings",size=8.5)
    for name,y,label in [
        ("n0",5.25,"$P'_0$ joins\npersists $z'_1,z'_2$"),
        ("n1",3.8,"$P_1$ persists\n$z'_0,z'_2$"),
        ("n2",2.35,"$P_2$ persists\n$z'_0,z'_1$")]:
        d.box(name,14.45,y,2.9,.95,label,size=8.5)
    d.box("cert",8.7,.75,14.65,1.0,
          "Public certificate: full context; $C_0,C_1,C_2$; $C'_0,C'_1,C'_2$; $D_1,D_2$;\n"
          "two survivor proposals; six persist-after-verify receipts (two holders per component)",size=8.5)
    d.edge("o1","d2",sa="e",sb="w");d.edge("o2","d1",sa="e",sb="w")
    d.arrow(d.point("d2","e"),(7.55,3.85))
    d.arrow(d.point("d1","e"),(7.55,3.15))
    for name in ("n0","n1","n2"):d.edge("eq",name,sa="e",sb="w")
    d.arrow(d.point("d2","n"),d.point("cert","w"),
            via=((5.25,6.7),(.15,6.7),(.15,.75)))
    d.arrow(d.point("d1","s"),(5.25,1.25))
    for name,lane,target in [("n0",17.15,1.01),("n1",16.85,.75),("n2",16.55,.49)]:
        d.arrow(d.point(name,"e"),(16.025,target),
                via=((lane,d.point(name,"e")[1]),(lane,target)))
    d.save(out,"continuity-protocol")

def main():
    parser=argparse.ArgumentParser(description="Draw the protocol's two declared relations.")
    parser.add_argument("--outdir",type=Path,default=Path(__file__).resolve().parents[1]/"paper"/"figures")
    args=parser.parse_args();args.outdir.mkdir(parents=True,exist_ok=True)
    durability(args.outdir);protocol(args.outdir)
if __name__=="__main__":main()
