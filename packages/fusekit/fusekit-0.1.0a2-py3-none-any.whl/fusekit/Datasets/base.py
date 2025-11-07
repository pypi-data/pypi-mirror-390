import collections
import math

class Metric():
    def __init__(self, input, label):
        self.input = input
        self.label = label

    def exact_match(self):   
        matched_tokens = 0
        for token_id in self.label:
            matched_tokens += 1 if token_id in self.input else 0

        return matched_tokens / len(self.label)

    def f1(self):
        input_tokens = collections.Counter(self.input)
        label_tokens = collections.Counter(self.label)

        common = input_tokens & label_tokens
        true_positives = sum(common.values())
        precision = true_positives / len(self.input) if self.input else 0
        recall = true_positives / len(self.label) if self.label else 0

        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def rouge_L(self):
        def lcs(seq1, seq2):
            n, m = len(seq1), len(seq2)
            dp = [[0] * (m + 1) for _ in range(n + 1)]
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    if seq1[i - 1] == seq2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                    else:
                        dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
            return dp[n][m]

        lcs_length = lcs(self.input, self.label)
        recall = lcs_length / len(self.label) if self.label else 0
        precision = lcs_length / len(self.input) if self.input else 0

        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def bleu(self, n=4):
        def ngrams(sequence, n):
            return [tuple(sequence[i:i + n]) for i in range(len(sequence) - n + 1)]

        weights = [0.25] * min(len(self.input), n)  # Equal weights for 1- to n-grams
        precisions = []

        for i in range(1, len(weights) + 1):
            input_ngrams = collections.Counter(ngrams(self.input, i))
            label_ngrams = collections.Counter(ngrams(self.label, i))

            overlap = sum((input_ngrams & label_ngrams).values())
            total = sum(input_ngrams.values())

            precisions.append(overlap / total if total > 0 else 0)

        if len(precisions) == 0 or min(precisions) == 0:
            return 0.0

        # Calculate geometric mean of precisions
        geometric_mean = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
        
        # Brevity penalty
        brevity_penalty = (
            math.exp(1 - len(self.label) / len(self.input))
            if len(self.input) < len(self.label)
            else 1
        )

        return brevity_penalty * geometric_mean
    
    def tree_edit_distance(self):
        

        dists = {gsample['sample']._metadata['dataset']: [] for gsample in val_results['all_samples']}
        dists2 = {gsample['sample']._metadata['dataset']: [] for gsample in val_results['all_samples']}
        for gsample in val_results['all_samples']:
            dname = gsample['sample']._metadata['dataset']
            # GET CONDITIONS
            if '<pseudo>' in gsample['gen_text']:
                gen_text = gsample['gen_text']
                gen_text = gen_text[gen_text.find('conditions:'):gen_text.find('</pseudo>')].strip().split('\n')[1:]
                gen_text = ' AND '.join('(' + x + ')' for x in gen_text)  # wrap in brackets and join with AND 
                ground_query = gsample['sample'].pseudocode
                ground_query = ground_query[ground_query.find('conditions:'):].strip().split('\n')[1:]
                ground_query = ' AND '.join('(' + x + ')' for x in ground_query)  # wrap in brackets and join with AND

            elif '<sql>' in gsample['gen_text']:
                gen_text = gsample['gen_text']
                gen_text = gen_text[gen_text.find('WHERE') + 5:gen_text.find('</sql>')].strip().split('\n')
                gen_text = ' AND '.join('(' + x + ')' for x in gen_text)  # wrap in brackets and join with AND
                ground_query = gsample['sample'].sql_query
                ground_query = ground_query[ground_query.find('WHERE') + 5:].strip().split('\n')
                ground_query = ' AND '.join('(' + x + ')' for x in ground_query)
            else:
                print('error cannot find pseudo or sql in gen_text')
                dists[dname].append(1000)
                dists2[dname].append(1000)
                continue
                
            dist, dist_norm = utils.conds_distance(ground_query, gen_text)
            dists[dname].append(dist)
            dists2[dname].append(dist_norm)

        results = []
        norm_results = []
        dists_keys = list(dists.keys())
        dists2_keys = list(dists2.keys())
        dists_keys.sort()
        dists2_keys.sort()

        for dname in dists_keys:
            result = (dname, sum(dists[dname]) / len(dists[dname]))
            if debug:
                print(dname, result)
            results.append(result)
        for dname in dists2_keys:
            result = (f'normalized {dname}', sum(dists2[dname]) / len(dists2[dname]))
            if debug:
                print('normalized', dname, result)
            norm_results.append(result)

        return (results, norm_results)


class SpecialTokens:
    def __init__(self, cls='', sep='\n', start='<s>', stop='</s>'):
        self.cls = cls
        self.sep = sep
        self.start = start
        self.stop = stop

class APICost():
    def __init__(self, input_cost, output_cost):
        self.input_cost = input_cost
        self.output_cost = output_cost

    def __add__(self, other):
        if isinstance(other, APICost):
            return APICost(self.input_cost + other.input_cost,
                           self.output_cost + other.output_cost)
        else:
            print("Error: All objects must be of class APICost")
            return self
        
    def __repr__(self):
        return f'Total Cost: ${self.input_cost + self.output_cost:0.6f} ' + \
               f'Input Cost: ${self.input_cost:0.6f}, Output Cost: ${self.output_cost:0.6f}'