import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import { cn } from '../../lib/utils';

export interface Segment {
  text: string;
  className?: string;
}

interface WordsPullUpMultiStyleProps {
  segments: Segment[];
  className?: string;
}

export function WordsPullUpMultiStyle({ segments, className }: WordsPullUpMultiStyleProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  // Flatten segments into words with their associated className
  const wordsWithStyles = segments.flatMap((segment) =>
    segment.text.split(' ').map((word) => ({ word, className: segment.className }))
  );

  return (
    <div
      ref={ref}
      className={cn("inline-flex flex-wrap justify-center", className)}
    >
      {wordsWithStyles.map((item, i) => (
        <motion.span
          key={i}
          initial={{ y: 20, opacity: 0 }}
          animate={isInView ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
          transition={{
            delay: i * 0.08,
            duration: 0.5,
            ease: [0.16, 1, 0.3, 1],
          }}
          className={cn("inline-block mr-[0.25em]", item.className)}
        >
          {item.word}
        </motion.span>
      ))}
    </div>
  );
}
