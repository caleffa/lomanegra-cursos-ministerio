export class Segment {
    public id: number;
    public title: string = null;
    public type_of_segment: string = null;
    public max_retries: number = null;
    public min_correct_questions: number = null;
    public order: number = null;
    public enabled_since: Date = null;
    public thumbnail: string = null;
    public vimeo_id: number = null;
}

export class SegmentSection {
    public id: number;
    public order: number = null;
    public questions_to_ask: number = null;
}

export class Question {
    public id: number;
    public text: string = null;
    public image: string = null;
    public has_only_one_correct_answer: boolean = null;
    public show_correct_options: number = null;
    public show_incorrect_options: number = null;
    public text_after_correct_answer: string = null;
    public text_after_incorrect_answer: string = null;
}

export class Option {
    public id: number;
    public text: string = null;
    public is_correct: boolean = true;
}

export class Slide {
    public id: number;
    public image: string = null;
}
