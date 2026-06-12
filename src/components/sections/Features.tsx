import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import { Code2, FileCode, Share2, Check, ArrowRight } from 'lucide-react';
import { WordsPullUpMultiStyle } from '../ui/WordsPullUpMultiStyle';

export function Features() {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: "-100px" });

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: (custom: number) => ({
      opacity: 1,
      scale: 1,
      transition: {
        delay: custom * 0.15,
        duration: 0.6,
        ease: [0.22, 1, 0.36, 1] as [number, number, number, number]
      }
    })
  };

  const headerSegments = [
    { text: "Your code. Always within reach.", className: "text-[#E1E0CC] text-xl sm:text-2xl md:text-3xl lg:text-4xl font-normal w-full" },
    { text: "Built for speed. Designed for clarity.", className: "text-gray-500 text-xl sm:text-2xl md:text-3xl lg:text-4xl font-normal w-full mt-2" }
  ];

  return (
    <section id="features" className="relative min-h-screen w-full bg-black py-20 px-4 md:px-6">
      {/* Noise Background */}
      <div className="absolute inset-0 bg-noise opacity-[0.15] pointer-events-none" />

      <div className="relative z-10 max-w-[1400px] mx-auto">
        <div className="text-center mb-16 md:mb-24 flex flex-col items-center">
          <WordsPullUpMultiStyle segments={headerSegments} className="flex-col items-center" />
        </div>

        <div 
          ref={containerRef}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-2 md:gap-1 lg:h-[480px]"
        >
          {/* Card 1 - Visual */}
          <motion.div
            custom={0}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            variants={cardVariants}
            className="relative rounded-2xl overflow-hidden min-h-[300px] lg:min-h-full"
          >
            <div 
              className="absolute inset-0 bg-cover bg-center"
              style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1542831371-29b0f74f9713")' }}
            />
            <div className="absolute inset-0 bg-black/40" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            <p className="absolute bottom-6 left-6 text-[#E1E0CC] font-medium">Your creative canvas.</p>
          </motion.div>

          {/* Card 2 */}
          <FeatureCard 
            custom={1}
            isInView={isInView}
            variants={cardVariants}
            number="01"
            title="Instant Search."
            icon={<Code2 className="w-8 h-8 text-[#E1E0CC]" />}
            features={[
              "Full text search across all snippets",
              "Filter by language or tags",
              "Results in under 50ms",
              "Keyboard shortcut support"
            ]}
          />

          {/* Card 3 */}
          <FeatureCard 
            custom={2}
            isInView={isInView}
            variants={cardVariants}
            number="02"
            title="Syntax Highlighting."
            icon={<FileCode className="w-8 h-8 text-[#E1E0CC]" />}
            features={[
              "20+ programming languages",
              "Shiki-powered rendering",
              "Dark and light themes"
            ]}
          />

          {/* Card 4 */}
          <FeatureCard 
            custom={3}
            isInView={isInView}
            variants={cardVariants}
            number="03"
            title="One-click Share."
            icon={<Share2 className="w-8 h-8 text-[#E1E0CC]" />}
            features={[
              "Public links with no login",
              "View count tracking",
              "Embed anywhere"
            ]}
          />
        </div>
      </div>
    </section>
  );
}

function FeatureCard({ custom, isInView, variants, number, title, icon, features }: any) {
  return (
    <motion.div
      custom={custom}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={variants}
      className="bg-[#212121] rounded-2xl p-6 md:p-8 flex flex-col h-full min-h-[350px] lg:min-h-full"
    >
      <div className="flex justify-between items-start mb-12">
        {icon}
        <span className="text-gray-500 text-xs font-mono">{number}</span>
      </div>
      
      <h3 className="text-[#E1E0CC] font-medium text-xl mb-6">{title}</h3>
      
      <ul className="space-y-4 mb-auto">
        {features.map((feature: string, i: number) => (
          <li key={i} className="flex items-start gap-3">
            <Check className="w-4 h-4 text-primary shrink-0 mt-0.5" />
            <span className="text-gray-400 text-sm">{feature}</span>
          </li>
        ))}
      </ul>
      
      <a href="#" className="inline-flex items-center gap-2 text-[#E1E0CC] text-sm font-medium mt-8 group">
        Learn more 
        <ArrowRight className="w-4 h-4 -rotate-45 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
      </a>
    </motion.div>
  );
}
