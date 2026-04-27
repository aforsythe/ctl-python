// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#pragma once
#include <string>
#include <vector>
#include <algorithm>

namespace ctlpython {

inline size_t levenshtein(const std::string& a, const std::string& b) {
    std::vector<size_t> prev(b.size() + 1), cur(b.size() + 1);
    for (size_t j = 0; j <= b.size(); ++j) prev[j] = j;
    for (size_t i = 1; i <= a.size(); ++i) {
        cur[0] = i;
        for (size_t j = 1; j <= b.size(); ++j) {
            size_t cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
            cur[j] = std::min({prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost});
        }
        std::swap(prev, cur);
    }
    return prev[b.size()];
}

inline std::string nearest_word(const std::string& q, const std::vector<std::string>& cand) {
    if (cand.empty()) return "";
    auto best = cand[0];
    size_t best_d = levenshtein(q, best);
    for (size_t i = 1; i < cand.size(); ++i) {
        size_t d = levenshtein(q, cand[i]);
        if (d < best_d) { best_d = d; best = cand[i]; }
    }
    if (best_d > std::max<size_t>(2, q.size() / 3)) return "";
    return best;
}

}
