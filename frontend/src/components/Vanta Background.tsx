import { useEffect, useRef } from 'react';

declare global {
  interface Window {
    VANTA: any;
    THREE: any;
  }
}

const VantaBackground = () => {
  const vantaRef = useRef<HTMLDivElement>(null);
  const vantaEffect = useRef<any>(null);

  useEffect(() => {
    if (!vantaRef.current) return;

    const initVanta = () => {
      if (window.VANTA && window.THREE) {
        vantaEffect.current = window.VANTA.GLOBE({
          el: vantaRef.current,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          color: 0x3b82f6,
          backgroundColor: 0xffffff
        });
      }
    };

    // Wait for scripts to load
    const checkScripts = setInterval(() => {
      if (window.VANTA && window.THREE) {
        clearInterval(checkScripts);
        initVanta();
      }
    }, 100);

    return () => {
      if (vantaEffect.current) {
        vantaEffect.current.destroy();
      }
      clearInterval(checkScripts);
    };
  }, []);

  return (
    <div 
      ref={vantaRef} 
      className="fixed top-0 left-0 w-full h-full -z-10 opacity-10"
    />
  );
};

export default VantaBackground;