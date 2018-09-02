
from controller.game import GameController
from model.aiplayer import AiPlayer
from model.config import Direction
from view.view import View
from fastai.conv_learner import *
from fastai.dataset import *
from fastai.plots import *


class DeepAiPlayer(AiPlayer):
    """ represents a AI-controlled player using a CNN for evaluating moves """

    def __init__(self, game: GameController, gui: View, name: str):
        super().__init__(game, gui, name)
        self.img_path = 'data/'
        sz = 256
        arch = resnet18
        data = ImageClassifierData.from_paths(self.img_path, tfms=tfms_from_model(arch, sz))
        self.learn = ConvLearner.pretrained(arch, data, precompute=False)
        self.learn.load('epoch10')
        trn_tfms, val_tfms = tfms_from_model(arch, sz)
        self.transforms = val_tfms

    def best_move(self, potential_moves):
        """ returns whatever the CNN considers the best move"""

        self.generate_images(potential_moves)
        prediction, best_move_index = self.perform_inference()
        #if prediction > 0.25:
        #    best_move = potential_moves[best_move_index]
        #else:
        #    return AiPlayer.best_move(self, #potential_moves)

        best_move = potential_moves[best_move_index]

        # now we've decided on a move, remove those tiles from the rack:
        if best_move.tiles:
            self.rack.get_tiles(''.join([str(t) for t in best_move.tiles]))

        # DEBUG:
        # print(self.name+": Best move is: "+str(best_move))  # DEBUG

        return best_move

    def generate_images(self, potential_moves):
        """ saves images for all possible moves for the CNN to consider """
        cached_rack = copy.deepcopy(self.game.active_player.rack)
        for i in range(len(potential_moves)):
            base_layer = copy.deepcopy(self.game.board.existing_letters[:-1, :-1])  # slice off last sentinel
            # set first sentinel squares to zero instead of sentinel value:
            base_layer[0, :] = 0
            base_layer[:, 0] = 0

            move_layer = np.zeros([16, 16], dtype='int')
            # put rack tiles we're playing from in first row:
            move_layer[0][0:len(cached_rack)] = [ord(t) - 64 for t in cached_rack.rack_tiles]

            # set first sentinel squares to zero instead of sentinel value:
            word_mult = np.where(self.game.board.word_multipliers > 1, self.game.board.word_multipliers * 8, 0)
            letter_mult = np.where(self.game.board.letter_multipliers > 1, self.game.board.letter_multipliers * 2, 0)
            score_layer = np.where(self.game.board.existing_letter_scores > 0,
                                   self.game.board.existing_letter_scores * 2,
                                   word_mult + letter_mult)
            score_layer = score_layer[:-1, :-1]  # slice off last sentinel
            # set first sentinel squares to zero instead of sentinel value:
            score_layer[0, :] = 0
            score_layer[:, 0] = 0

            move = potential_moves[i]
            move_tiles = move.tiles if move.tiles else []

            if move.direction == Direction.NOT_APPLICABLE:  # pass or exchange
                # put rack tiles we're exchanging in first row:
                if move.tiles:  # unless it's a pass with no tiles
                    move_layer[0][0:len(move_tiles)] = [ord(t) - 64 for t in move.tiles]

            else:  # regular move
                row = move_layer[move.row.rank, :] if move.direction == Direction.HORIZONTAL else move_layer[:,
                                                                                                  move.row.rank]
                # put rack tiles we're playing on board:
                row[move.played_squares] = [ord(t) - 64 for t in move.tiles]
                # change score of square containing blank to zero:
                score_layer = np.where(move_layer <= 26, score_layer, 0)
                # change blanks to normal letter ordinal (by subtracting 32)
                move_layer = np.where(move_layer <= 26, move_layer, move_layer - 32)

            # flatten arrays and convert int8 to int so values aren't clipped at 128:
            rgb = zip((base_layer.astype(int)).flatten() * 9, (score_layer.astype(int)).flatten() * 9,
                      (move_layer.astype(int)).flatten() * 9)
            # put in a list:
            rgb = [pixel for pixel in rgb]

            # convert to an image
            img = Image.new('RGB', (16, 16))
            img.putdata(rgb)

            # save the image
            img.save(self.img_path + 'temp/option_' + str(i).zfill(4) + '.png')

    def perform_inference(self):
        """ assess each image by doing a forward pass through the CNN """
        image_paths = [self.img_path + 'temp/' + file_name for file_name in os.listdir(self.img_path + 'temp')]
        images = [self.transforms(open_image(image_path)) for image_path in image_paths]
        [os.remove(image_path) for image_path in image_paths] # delete temp files
        #predictions = [np.exp(self.learn.predict_array(img[None])[0][0]) for img in images]
        predictions = [np.exp(self.learn.predict_array(img[None])[0][0]) for img in images]
        best_image_index = np.argmax(predictions)
        prediction = predictions[best_image_index]
        return (prediction, best_image_index)
