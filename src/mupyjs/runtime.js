function set_properties(dst, props) {
    for (const [key, value] of Object.entries(props)) {
        Object.defineProperty(dst, key, {
            value: value,
            writable: true,
            enumerable: false,
            configurable: true
        });
    }
}
set_properties(Number.prototype, {
    __add__(other) {
        return this + other;
    },
    __sub__(other) {
        return this - other;
    },
    __mul__(other) {
        return this * other;
    },
    __truediv__(other) {
        return this / other;
    },
    __floordiv__(other) {
        return Math.floor(this / other);
    },
    __mod__(other) {
        return this % other;
    },
    __pow__(other) {
        return Math.pow(this, other);
    },
    __eq__(other) {
        return this === other;
    },
    __ne__(other) {
        return this !== other;
    },
    __lt__(other) {
        return this < other;
    },
    __le__(other) {
        return this <= other;
    },
    __gt__(other) {
        return this > other;
    },
    __ge__(other) {
        return this >= other;
    },
});
set_properties(Object.prototype, {
    __getattr__(name) {
        return this[name];
    },
    __setattr__(name, value) {
        this[name] = value;
    },
    __getitem__(name) {
        return this[name];
    },
    __setitem__(name, value) {
        this[name] = value;
    },
    __eq__(other) {
        return this === other;
    },
    __ne__(other) {
        return this !== other;
    },
}); 

set_properties(String.prototype, {
    __add__(other) {
        return this + other;
    },
    __getitem__(index) {
        return this[index];
    },
    __setitem__(index, value) {
        this[index] = value;
    },
});

export function print(...args) {
    console.log(...args);
}

export function list(o) {
    return Array.from(o);
}

export function* range(start, end, step) {
    if (step === undefined) {
        step = 1;
    }
    if( end === undefined) {
        end = start;
        start = 0;
    }
    for (let i = start; i < end; i += step) {
        yield i;
    }
}