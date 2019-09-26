"use strict";

const e = React.createElement;

class Button extends React.Component {
    render() {
        return e(
            "button",
            {
                id: this.props.id_prefix + "_button",
                onClick: this.props.onClick,
            },
            this.props.button_text
        );
    }
}

class TextInput extends React.Component {
    render() {
        return e(
            "input",
            {
                id: this.props.id,
                name: this.props.name,
                type: "text",
                placeholder: this.props.placeholder,
                value: this.props.initialValue,
                onChange: this.props.onChange,
            }
        );
    }
}

class DateInput extends React.Component {
    render() {
        return e(
            "input",
            {
                id: this.props.id,
                name: this.props.name,
                type: "date",
                defaultValue: this.props.initialValue,
                onChange: this.props.onChange,
            }
        );
    }
}

class FormElement extends React.Component {
    render() {
        let label = null;
        if (!this.props.without_label) {
            label = e(
                "label",
                {
                    htmlFor: this.props.id_prefix,
                },
                this.props.label_text
            );
        }

        return e(
            "div",
            {
                id: this.props.id_prefix + "_formelement",
                className: "formelement",
            },
            [
                label,
                this.props.children,
            ]
        );
    }
}

class WeatherDoyForm extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleOnChange = this.handleOnChange.bind(this);

        this.state = {
            address: "",
            date: new Date(),
        };
    }

    handleOnChange(event) {
        let valueAccessor = (target) => target.value;

        if (event.target.type === "date") {
            valueAccessor = (target) => target.valueAsDate;
        }

        this.setState(
            {
                [event.target.name]: valueAccessor(event.target),
            }
        );
    }

    handleSubmit(event) {
        event.preventDefault();

        const formattedDate = formatDate(this.state.date);
        if (this.state.address === "" || formattedDate === "") {
            alert("Both address and date must be filled!");
            return;
        }

        getWeatherForDayOfYearAtAddressHtml(this.state.address, formattedDate, (resultHtml) => {
            this.props.displayResult(resultHtml);
        });
    }

    render() {
        const initialDateString = this.state.date.toISOString().substr(0, 10);

        return e(
            "form",
            {
                id: "form_weather_for_day_of_year_at_address",
                className: "form",
            },
            [
                e(
                    FormElement,
                    {
                        id_prefix: "address",
                        label_text: "Address:",
                    },
                    e(
                        TextInput,
                        {
                            id: "address",
                            name: "address",
                            placeholder: "E.g. Schwetzinger Schloss",
                            initialValue: this.address,
                            onChange: this.handleOnChange,
                        }
                    )
                ),
                e(
                    FormElement,
                    {
                        id_prefix: "date",
                        label_text: "Date:",
                    },
                    e(
                        DateInput,
                        {
                            id: "date",
                            name: "date",
                            initialValue: initialDateString,
                            onChange: this.handleOnChange,
                        }
                    )
                ),
                e(
                    FormElement,
                    {
                        id_prefix: "submit",
                        without_label: true,
                    },
                    e(
                        Button,
                        {
                            id_prefix: "submit",
                            button_text: "Submit",
                            onClick: this.handleSubmit,
                        }
                    )
                ),
            ]
        );
    }
}

class ResultContainer extends React.Component {
    render() {
        return e(
            "div",
            {
                id: "result_container",
                dangerouslySetInnerHTML: {
                    __html: this.props.resultHTML,
                },
            }
        )
    }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.handleDisplayResult = this.handleDisplayResult.bind(this);
        this.state = {
            resultHTML: null,
        };
    }

    handleDisplayResult(result) {
        this.setState({
            resultHTML: result,
        });
    }
    
    render() {
        return e(
            "div",
            {},
            [
                e(WeatherDoyForm, {displayResult: this.handleDisplayResult}),
                e(ResultContainer, {resultHTML: this.state.resultHTML}),
            ]
        );
    }
}

const domContainer = document.querySelector("#app_container");
ReactDOM.render(e(App), domContainer);
