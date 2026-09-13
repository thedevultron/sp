import { EyebrowLabel } from "../ui/EyebrowLabel";
import { Reveal } from "../ui/Reveal";
import { ScrollFloat } from "../cinematic/TextMotion";
import FoldText from "../FoldText";
import { LiveTypingPlayground } from "../simulator/LiveTypingPlayground";

export function SimulatorSection() {
  return (
    <section id="simulator" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-[1200px] px-6">
        <ScrollFloat>
          <Reveal>
            <EyebrowLabel>Live test drive</EyebrowLabel>
          </Reveal>
          <h2 className="mx-auto mt-6 max-w-[18ch] text-center font-display text-4xl font-medium tracking-tight sm:text-5xl">
            <FoldText
              text="Press it. Watch it type."
              splitBy="word"
              hinge="top"
              trigger="scroll"
              duration={0.6}
              stagger={0.035}
              ease="power3.out"
              fontSize="1em"
              fontWeight={500}
              color="#d1e4fa"
              style={{ lineHeight: "1.14", letterSpacing: "-0.01em" }}
            />
          </h2>
          <Reveal delay={0.14}>
            <p className="mx-auto mt-6 max-w-[58ch] text-center text-[15.5px] leading-relaxed text-fog">
              Pick a target window. Pick raw or refined. Hit the button or hold your own{" "}
              <span className="font-mono text-[13px] text-mist">Ctrl + Space</span>. You watch
              text land where the caret sits.
            </p>
          </Reveal>
        </ScrollFloat>

        <Reveal delay={0.18} y={36} className="mt-14">
          <LiveTypingPlayground />
        </Reveal>
      </div>
    </section>
  );
}
