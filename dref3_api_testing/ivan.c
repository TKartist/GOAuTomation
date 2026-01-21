#ifndef LIFE_H
#define LIFE_H

#define CELL_DEAD  0
#define CELL_LIVE  1
#define CELL_ERROR (-1)

struct life;

struct life *create_bounded(int left, int bottom, int right, int top);
struct life *create_folded(int width, int height);

struct life *copy(const struct life *l);
void destroy(struct life *l);

int get(const struct life *l, int x, int y);
int set(struct life *l, int x, int y, int status);

void next_gen(struct life *l);

#endif

#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "life.h"

enum life_kind { LIFE_BOUNDED = 1, LIFE_FOLDED = 2 };

struct life {
    enum life_kind kind;
    int left, bottom, right, top;
    int width, height;
    unsigned char *cells;
};

static int checked_mul_size_t(size_t a, size_t b, size_t *out) {
    if (a == 0 || b == 0) { 
        *out = 0; 
        return 1; 
    }
    if (a > (SIZE_MAX / b)) return 0;
    *out = a * b;
    return 1;
}

static void dims_of(const struct life *l, int *w, int *h) {
    if (l->kind == LIFE_BOUNDED) {
        *w = l->right - l->left + 1;
        *h = l->top - l->bottom + 1;
    } else {
        *w = l->width;
        *h = l->height;
    }
}

static int valid_coord(const struct life *l, int x, int y) {
    if (l->kind == LIFE_BOUNDED) {
        return (x >= l->left && x <= l->right && y >= l->bottom && y <= l->top);
    } else {
        return (x >= 0 && x < l->width && y >= 0 && y < l->height);
    }
}

static size_t idx_of(const struct life *l, int x, int y) {
    int w, h;
    (void)h;
    dims_of(l, &w, &h);

    if (l->kind == LIFE_BOUNDED) {
        int xx = x - l->left;
        int yy = y - l->bottom;
        return (size_t)yy * (size_t)w + (size_t)xx;
    } else {
        return (size_t)y * (size_t)w + (size_t)x;
    }
}

static int wrap_mod(int v, int m) {
    int r = v % m;
    if (r < 0) r += m;
    return r;
}

struct life *create_bounded(int left, int bottom, int right, int top) {
    int w = right - left + 1;
    int h = top - bottom + 1;
    if (w <= 0 || h <= 0) return NULL;

    size_t n;
    if (!checked_mul_size_t((size_t)w, (size_t)h, &n)) return NULL;

    struct life *l = (struct life *)malloc(sizeof(*l));
    if (!l) return NULL;

    l->kind = LIFE_BOUNDED;
    l->left = left;
    l->bottom = bottom;
    l->right = right;
    l->top = top;
    l->width = 0;
    l->height = 0;

    l->cells = (unsigned char *)calloc(n, 1);
    if (!l->cells) {
        free(l);
        return NULL;
    }
    return l;
}

struct life *create_folded(int width, int height) {
    /* Paper says: you may assume width and height > 0 */
    if (width <= 0 || height <= 0) return NULL; /* defensive */

    size_t n;
    if (!checked_mul_size_t((size_t)width, (size_t)height, &n)) return NULL;

    struct life *l = (struct life *)malloc(sizeof(*l));
    if (!l) return NULL;

    l->kind = LIFE_FOLDED;
    l->left = l->bottom = l->right = l->top = 0;
    l->width = width;
    l->height = height;

    l->cells = (unsigned char *)calloc(n, 1);
    if (!l->cells) {
        free(l);
        return NULL;
    }
    return l;
}

/* ------------------------- Copy / Destroy ------------------------- */

struct life *copy(const struct life *src) {
    if (!src) return NULL;

    int w, h;
    dims_of(src, &w, &h);

    size_t n;
    if (!checked_mul_size_t((size_t)w, (size_t)h, &n)) return NULL;

    struct life *dst = (struct life *)malloc(sizeof(*dst));
    if (!dst) return NULL;

    *dst = *src; /* copies fields (including pointers), will fix pointer next */

    dst->cells = (unsigned char *)malloc(n);
    if (!dst->cells) {
        free(dst);
        return NULL;
    }
    memcpy(dst->cells, src->cells, n);
    return dst;
}

void destroy(struct life *l) {
    if (!l) return;
    free(l->cells);
    free(l);
}

/* ------------------------- get / set ------------------------- */

int get(const struct life *l, int x, int y) {
    if (!l) return CELL_ERROR;

    if (!valid_coord(l, x, y)) return CELL_ERROR;

    size_t idx = idx_of(l, x, y);
    return l->cells[idx] ? CELL_LIVE : CELL_DEAD;
}

int set(struct life *l, int x, int y, int status) {
    if (!l) return CELL_ERROR;

    if (!valid_coord(l, x, y)) return CELL_ERROR;
    if (!(status == CELL_LIVE || status == CELL_DEAD)) return CELL_ERROR;

    size_t idx = idx_of(l, x, y);
    l->cells[idx] = (unsigned char)(status == CELL_LIVE ? 1 : 0);
    return status;
}

/* ------------------------- next_gen ------------------------- */

static int neighbor_count_bounded(const struct life *l, int x, int y) {
    int cnt = 0;
    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            if (dx == 0 && dy == 0) continue;
            int nx = x + dx;
            int ny = y + dy;
            if (!valid_coord(l, nx, ny)) continue; /* outside is always dead */
            size_t idx = idx_of(l, nx, ny);
            cnt += (l->cells[idx] != 0);
        }
    }
    return cnt;
}

static int neighbor_count_folded(const struct life *l, int x, int y) {
    int cnt = 0;
    int w = l->width, h = l->height;
    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            if (dx == 0 && dy == 0) continue;
            int nx = wrap_mod(x + dx, w);
            int ny = wrap_mod(y + dy, h);
            size_t idx = idx_of(l, nx, ny);
            cnt += (l->cells[idx] != 0);
        }
    }
    return cnt;
}

void next_gen(struct life *l) {
    if (!l) return;

    int w, h;
    dims_of(l, &w, &h);

    size_t n;
    if (!checked_mul_size_t((size_t)w, (size_t)h, &n)) return; /* defensive */

    unsigned char *next = (unsigned char *)calloc(n, 1);
    if (!next) return; /* paper doesn’t specify error reporting; just do nothing */

    if (l->kind == LIFE_BOUNDED) {
        for (int y = l->bottom; y <= l->top; y++) {
            for (int x = l->left; x <= l->right; x++) {
                size_t idx = idx_of(l, x, y);
                int alive = (l->cells[idx] != 0);
                int nb = neighbor_count_bounded(l, x, y);

                /* Classic Life rules */
                int out_alive = 0;
                if (alive) out_alive = (nb == 2 || nb == 3);
                else       out_alive = (nb == 3);

                next[idx] = (unsigned char)(out_alive ? 1 : 0);
            }
        }
    } else { /* LIFE_FOLDED */
        for (int y = 0; y < l->height; y++) {
            for (int x = 0; x < l->width; x++) {
                size_t idx = idx_of(l, x, y);
                int alive = (l->cells[idx] != 0);
                int nb = neighbor_count_folded(l, x, y);

                int out_alive = 0;
                if (alive) out_alive = (nb == 2 || nb == 3);
                else       out_alive = (nb == 3);

                next[idx] = (unsigned char)(out_alive ? 1 : 0);
            }
        }
    }

    free(l->cells);
    l->cells = next;
}
