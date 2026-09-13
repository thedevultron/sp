import { useCallback, useEffect, useState } from 'react';
import Lenis from '@studio-freight/lenis';
import { useReducedMotion } from 'framer-motion';
import { ArrowUpRight, Menu, X } from 'lucide-react';
import { WaveLogo } from './components/ui/Primitives';
import ProductModal from './components/ui/ProductModal';
import { HeroSection, PipelineSection, SimulatorSection, BentoPillarsSection, HotkeysSecuritySection, DownloadFooterSection } from './components/sections/ProductSections';
import './styles/authkit-tokens.css';
import './styles/globals.css';

type ModalType = 'settings' | 'guide' | 'download' | 'support' | null;
export default function App() {
 const [modal,setModal]=useState<ModalType>(null);
 const [menu,setMenu]=useState(false);
 const [activeSection,setActiveSection]=useState('overview');
 const [demo,setDemo]=useState({active:false,text:'',progress:12});
 const reduced=useReducedMotion();
 const closeModal=useCallback(()=>setModal(null),[]);
 const updateDemo=useCallback((s:typeof demo)=>setDemo(s),[]);
 useEffect(()=>{ if(reduced) return; const lenis=new Lenis({duration:1.15,smoothWheel:true}); let id=0; const frame=(time:number)=>{lenis.raf(time);id=requestAnimationFrame(frame);};id=requestAnimationFrame(frame); const onScroll=()=>{document.documentElement.style.setProperty('--scroll-depth',`${Math.min(window.scrollY*.13,130)}px`);}; window.addEventListener('scroll',onScroll,{passive:true}); return()=>{cancelAnimationFrame(id);lenis.destroy();window.removeEventListener('scroll',onScroll);}; },[reduced]);
 useEffect(()=>{const observer=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting)setActiveSection(e.target.id);});},{rootMargin:'-10% 0px -65% 0px'});document.querySelectorAll('section[id]').forEach(s=>observer.observe(s));return()=>observer.disconnect();},[]);
 const links=[['Overview','overview'],['How it works','how-it-works'],['Features','features'],['Privacy','privacy']];
 return <><header className="site-header"><div className="nav-inner"><a href="#overview" className="brand" aria-label="SPEAK home"><WaveLogo small/><span>SPEAK</span><span className="nav-version">v2.0</span></a><nav className={menu?'main-nav open':'main-nav'} aria-label="Main navigation">{links.map(([label,id])=><a key={id} href={`#${id}`} className={activeSection===id?'active':''} onClick={()=>setMenu(false)}>{label}</a>)}</nav><div className="nav-actions"><span className="free-status"><span className="status-dot"/>Free. Forever.</span><button className="nav-download" onClick={()=>setModal('download')}>Get SPEAK<ArrowUpRight size={14}/></button><button className="menu-toggle" aria-label={menu?'Close menu':'Open menu'} aria-expanded={menu} onClick={()=>setMenu(!menu)}>{menu?<X size={21}/>:<Menu size={21}/>}</button></div></div></header><main><HeroSection demo={demo} onModal={setModal}/><div className="page-content"><PipelineSection/><SimulatorSection onUpdate={updateDemo}/><BentoPillarsSection/><HotkeysSecuritySection/><DownloadFooterSection onModal={setModal}/></div></main><ProductModal type={modal} onClose={closeModal}/></>;
}
