from manim import *

class TransformerArchitecture(Scene):
    def construct(self):
        title = Text("Transformer Architecture", font_size=40).to_edge(UP)
        self.play(Write(title))

        encoder = Rectangle(width=2, height=3, color=BLUE, fill_opacity=0.5)
        encoder_label = Text("Encoder", font_size=24).move_to(encoder.get_center())
        encoder_group = VGroup(encoder, encoder_label).shift(LEFT * 3)

        decoder = Rectangle(width=2, height=3, color=GREEN, fill_opacity=0.5)
        decoder_label = Text("Decoder", font_size=24).move_to(decoder.get_center())
        decoder_group = VGroup(decoder, decoder_label).shift(RIGHT * 3)

        self.play(Create(encoder), Write(encoder_label))
        self.play(Create(decoder), Write(decoder_label))

        arrow1 = Arrow(start=encoder.get_right(), end=decoder.get_left(), buff=0.1, color=YELLOW)
        attention_text = Text("Cross Attention", font_size=20).next_to(arrow1, UP)
        
        self.play(GrowArrow(arrow1), Write(attention_text))

        input_arrow = Arrow(start=DOWN * 3 + LEFT * 3, end=encoder.get_bottom(), buff=0.1)
        input_text = Text("Inputs", font_size=20).next_to(input_arrow, DOWN)
        
        output_arrow = Arrow(start=decoder.get_top(), end=UP * 2.5 + RIGHT * 3, buff=0.1)
        output_text = Text("Outputs", font_size=20).next_to(output_arrow, UP)

        self.play(GrowArrow(input_arrow), Write(input_text))
        self.play(GrowArrow(output_arrow), Write(output_text))
        
        self.wait(2)
